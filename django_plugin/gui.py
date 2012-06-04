# -*- coding: utf-8 *-*
import logging

from PyQt4.QtGui import QTreeWidget
from PyQt4.QtGui import QTreeWidgetItem
from PyQt4.QtGui import QHeaderView
from PyQt4.QtGui import QAbstractItemView
from PyQt4.QtCore import SIGNAL

from ninja_ide.gui.explorer.explorer_container import ExplorerContainer
from ninja_ide.core import plugin
from ninja_ide.core.plugin_interfaces import IProjectTypeHandler
from ninja_ide.core.plugin_interfaces import implements
from ninja_ide.core.file_manager import belongs_to_folder

from template_parser.context import get_context

from copy import deepcopy
from collections import namedtuple
import re

from django.template import Template
from django.conf import settings

logger = logging.getLogger('ninja-django-plugin.django_plugin.gui')
logging.basicConfig()
logger.setLevel(logging.DEBUG)
DEBUG = logger.debug

settings.configure(TEMPLATE_DIRS=tuple())
Node = namedtuple('Node', ['value', 'children'])
TEMPLATE_RE = re.compile("\{\{.+?\}\}")
PROJECT_TYPE = "Django App"


class DjangoContextItem(object):
    def __init__(self, item):
        self.__item = item

    def __len__():
        return 0


def parse_django_template(text):
    template = Template(text)
    return get_context(template)


class DjangoContext(object):
    """A Mock object that constructs a template like context with a list
    of the variables used in such template thus providing the required
    context for it to be rendered.
    """

    def __init__(self, context_text=""):
        self._model = dict()
        self._context_list = []
        self.update_context(context_text)
        self._process_context_list()

    def __iter__(self):
        for each_child in self._model:
            yield each_child

    def __getitem__(self, key):
        return self._model[key]

    def update_context(self, context_text):
        context_list = parse_django_template(context_text)
        current, new = set(self._context_list), set(context_list)
        new = new.difference(current)
        if new:
            self._context_list = self._context_list + list(new)
            self._process_context_list()

    def set_context(self, context_text):
        context_list = parse_django_template(context_text)
        self._context_list = context_list
        self._model = dict()
        self._process_context_list(context_list)

    def get_context(self):
        """Serialize current tree and return context in list form"""
        return self._serialize_context_tree()

    context = property(get_context, set_context)

    def _process_context_list(self):
        """Take a list of paths and transform it into a tree structure"""
        self._context_list.sort()
        empty_node = Node(None, {})
        empty_node = dict(value=None, children=dict())
        for each_item in self._context_list:
            paths = each_item.split('.')
            branch = self._model
            for path in paths:
                node = branch.setdefault(path, deepcopy(empty_node))
                branch = node.get("children")

    def _serialize_context_list(self):
        """Tranform the current context tree and transform it into context"""
        context = []
        for each_item in self._model:
            context.append(each_item)
            for each_tree_path in self._walk_tree(self._model[each_item]):
                path = [each_item] + [each_tree_path]
                context.append(".".join(path))
        return context

    def _walk_tree(self, parent):
        """Recursively walk the tree to reconstruct the path"""
        if parent.value:
            yield parent.value
        children = parent.children
        if children:
            for each_child in children:
                yield each_child
                for each_path in self._walk_tree(children[each_child]):
                    path = [each_child] + [each_path]
                    path = [a_segment for a_segment in path if a_segment]
                    yield ".".join(path)
        else:
            yield None


class DjangoContextTreeItem(QTreeWidgetItem):
    def __init__(self, parent, name, node):
        QTreeWidgetItem.__init__(self, parent)
        self.setText(0, name)
        self._node = node
        value = node.get("value") and node.get("value") or ""
        self.setText(1, value)
        self._recurse_children()

    def _recurse_children(self):
        children = self._node.get("children", {})
        for each_child in children:
            DjangoContextTreeItem(self, each_child, children[each_child])

    def value_changed(self):
        self._node["value"] = self.text(1)


class DjangoContextExplorer(QTreeWidget):
    def __init__(self, context=None):
        QTreeWidget.__init__(self)
        self._editing = None
        self._context = context
        self.setSelectionMode(QTreeWidget.SingleSelection)
        self.setAnimated(True)
        self.header().setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.header().setResizeMode(0, QHeaderView.ResizeToContents)
        self.header().setStretchLastSection(False)
        self.setColumnCount(2)
        self.setHeaderLabels(("Label", "Value"))
        s_dclicked = "itemDoubleClicked(QTreeWidgetItem *, int)"
        self.connect(self, SIGNAL(s_dclicked), self.double_clicked_item)
        s_ichanged = "itemChanged(QTreeWidgetItem *, int)"
        self.connect(self, SIGNAL(s_ichanged), self.item_changed)
        s_iclicked = "itemClicked(QTreeWidgetItem *, int)"
        self.connect(self, SIGNAL(s_iclicked), self.item_clicked)

    def populate(self, context=None):
        if context:
            self._context = context
        self.clear()
        for each_item in self._context:
            DjangoContextTreeItem(self, each_item, self._context[each_item])

    def double_clicked_item(self, item, column):
        if column == 1:
            if self._editing:
                self.closePersistentEditor(*self._editing)
            self._editing = (item, column)
            self.openPersistentEditor(item, column)
        elif self._editing:
            self.closePersistentEditor(*self._editing)
            self._editing = None

    def item_changed(self, item, column):
        if self._editing:
            self.closePersistentEditor(item, column)
            item.value_changed()
            self._editing = None

    def item_clicked(self, item, column):
        if self._editing and (item != self._editing[0]):
            self.closePersistentEditor(*self._editing)
            self._editing = None


@implements(IProjectTypeHandler)
class DjangoProjectType(object):
    def __init__(self, locator):
        self.locator = locator

    def get_pages(self):
        """
        Returns a collection of QWizardPage
        """
        pass

    def on_wizard_finish(self, wizard):
        """
        Called when the user finish the wizard
        @wizard: QWizard instance
        """
        pass

    def get_context_menus(self):
        """"
        Returns a iterable of QMenu
        """
        return tuple()


class DjangoPluginMain(plugin.Plugin):
    def initialize(self, *args, **kwargs):
        ec = ExplorerContainer()
        super(DjangoPluginMain, self).initialize(*args, **kwargs)
        self._c_explorer = DjangoContextExplorer()
        self._contexts = dict()
        ec.addTab(self._c_explorer, "Django Template")
        editor_service = self.locator.get_service("editor")
        editor_service.currentTabChanged.connect(self._current_tab_changed)
        editor_service.fileSaved.connect(self._a_file_saved)

        self.explorer_s = self.locator.get_service('explorer')
        # Set a project handler for NINJA-IDE Plugin
        self.explorer_s.set_project_type_handler(PROJECT_TYPE,
                DjangoProjectType(self.locator))
        self._current_tab_changed(editor_service.get_editor_path())

    def _is_django_project(self, fileName):
        fileName = unicode(fileName)
        projects_obj = self.explorer_s.get_opened_projects()
        for each_project in projects_obj:
            if belongs_to_folder(unicode(each_project.path), fileName):
                return each_project.projectType == PROJECT_TYPE

    def _is_template(self, fileName):
        fileName = unicode(fileName)
        if self._is_django_project(fileName) and TEMPLATE_RE.findall(
                self.locator.get_service("editor").get_text()):
            return True

    def _load_context_for(self, context_key):
        current_text = self.locator.get_service("editor").get_text()
        if self._contexts.get(context_key, None):
            self._contexts[context_key].update_context(current_text)
        else:
            self._contexts[context_key] = DjangoContext(current_text)

    def _a_file_saved(self, fileName):
        fileName = unicode(fileName)
        if self._is_template(fileName):
            self._load_context_for(fileName)
            self._c_explorer.populate(self._contexts[fileName])

    def _current_tab_changed(self, fileName):
        fileName = unicode(fileName)
        DEBUG("Current tab changed to %s" % fileName)
        if self._is_template(fileName):
            if not (fileName in self._contexts):
                self._load_context_for(fileName)
            self._c_explorer.populate(self._contexts[fileName])
        else:
            self._c_explorer.clear()

    def finish(self):
        super(DjangoPluginMain, self).finish()

    def get_preferences_widget(self):
        return super(DjangoPluginMain, self).get_preferences_widget()

    def get_pages(self):
        """
        Should Returns a collection of QWizardPage or subclass
        """
        return super(DjangoPluginMain).get_pages()

    def on_wizard_finish(self, wizard):
        """
        Called when the user finish the wizard
        """
        super(DjangoPluginMain).on_wizard_finish()

    def get_context_menus(self):
        """"
        Should Returns an iterable of QMenu for the context type of the new
        project type
        """
        return super(DjangoPluginMain).get_context_menus()
