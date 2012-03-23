from collections import namedtuple

from django.template.base import Node, TextNode, VariableNode
from django.template.defaulttags import (
    CycleNode, FilterNode, FirstOfNode, LoadNode, NowNode, SpacelessNode,
    URLNode, WidthRatioNode)

# This import (loader) is required to make the next one (loader_tags) work:
import django.template.loader
from django.template.loader_tags import BlockNode

_NodeListWrapper = namedtuple("NodeListWrapper", "nodelist")


def _get_vars(filter_expression):
    """
    Return the list of vars used in a django filter expressions. That includes
    the main var and any filter arguments
    """
    if not hasattr(filter_expression.var, 'var'):
        # Probably a string literal or something like that
        result = []
    else:
        result = [filter_expression.var.var]
    for _, arglist in filter_expression.filters:
        result.extend(arg.var for lookup, arg in arglist if lookup)
    return result


def _get_node_context(node):
    """
    Return the list of vars used in a node
    """
    result = []
    # Ignored nodes
    if isinstance(node, (TextNode, BlockNode, NowNode, LoadNode, SpacelessNode)):
        pass
    # Simple variables
    elif isinstance(node, VariableNode):
        result = _get_vars(node.filter_expression)
    # Tags with arguments or some other magic
    elif isinstance(node, CycleNode):
        for expr in node.cyclevars:
            result += _get_vars(expr)
    elif isinstance(node, FilterNode):
        # The filter expr gets a "var|" prepended; so we remove it
        # with [1:]
        result = _get_vars(node.filter_expr)[1:]
    elif isinstance(node, FirstOfNode):
        for expr in node.vars:
            result += _get_vars(expr)
    elif isinstance(node, URLNode):
        if not node.legacy_view_name:  # Django 1.3 new url tag
            result += _get_vars(node.view_name)
        for arg in node.args:
            result += _get_vars(arg)
        for key, arg in node.kwargs.items():
            result += _get_vars(arg)
    elif isinstance(node, WidthRatioNode):
        result = _get_vars(node.val_expr) + \
                 _get_vars(node.max_expr) + \
                 _get_vars(node.max_width)
    else:
        assert False, "Unrecognized node %s" % type(node)

        # TODO: extends (hard, it's not just the argument but the template should be loaded too)
        # TODO: for (hard, the iterable, but also the renamings; then the contents. Also, the forllop stuff)
        # TODO: if (the expression, and then the contents on each branch
        # TODO: ifequal, ifnotequal
        # TODO: include (the argument and the content. also the renamings)
        # TODO: regroup (the arg, and renamings)
        # TODO: with: renamings

    # Go through children nodes. [1:] is to skip self
    for child in node.get_nodes_by_type(Node)[1:]:
        result += _get_node_context(child)

    return result

def get_context(template):
    """
    Returns a list of context variables used in the template. Each variable is
    represented as a dotted string from the context root.

    The argument is a template object, not just a filename.

    For example, passing the template {{ var }} {{ var.attribute }}
    Results in: ["var", "var.attribute"]

    And {% with local=var.attribute %}local.inner{% endwith %}
    Results in: ["var", "var.attribute", "var.attribute.inner"]

    Custom template tags may not be interpreted correctly, but any argument
    to a template tag that isn't quoted is used as a variable.
    """

    result = []
    for node in template.nodelist:
        result += _get_node_context(node)

    return result
