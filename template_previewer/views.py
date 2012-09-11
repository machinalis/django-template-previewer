import json

from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST, require_GET
from django.template.response import TemplateResponse
from django.core.urlresolvers import reverse
from django.template import Template, Context, loader, TemplateDoesNotExist

from template_previewer.forms import RenderForm, ParseForm
from template_previewer.template_parser.context import get_context

class ContextItem(object):
    def __init__(self, context_dict):
        self._context_dict = context_dict
        self._str = context_dict.pop("_str", "")
        self._len = 0
        while str(self._len) in context_dict:
            self._len += 1
        self._islist = self._len > 0

    def __str__(self):
        return self._str.encode('utf-8')

    def __unicode__(self):
        return self._str

    def __getitem__(self, key):
        if isinstance(key, int):
            key = str(key)
        return self._context_dict[key]

    def __iter__(self):
        if self._islist:
            return (self[str(x)] for x in range(self._len))
        else:
            return iter(self._context_dict)

    def __len__(self):
        return len(self._context_dict)

    def __int__(self):
        return int(self._str)

    def __float__(self):
        return float(self._str)


@require_POST
def render(request):
    """This is the actually preview, rendered on an <iframe>"""
    form = RenderForm(request.POST)
    if form.is_valid():
        template_name = form.cleaned_data['template']
        template = loader.get_template(template_name)
        decoder = json.JSONDecoder('utf-8', ContextItem)
        context = decoder.decode(form.cleaned_data['context'])
        c = Context(context)
        return HttpResponse(template.render(c))
    else:
        return HttpResponseBadRequest()

# The following are auxiliar functions to help making the tree out of the 
# parsed context in the template

def _make_node(name):
    return {
        "name": name,
        "children": []
    }

def _lookup(childlist, name):
    for child in childlist:
        if child["name"] == name: return child
    new = _make_node(name)
    childlist.append(new)
    return new

def _extend(childlist, path):
    path_items = path.split('.')
    for p in path_items:
        childlist = _lookup(childlist, p)["children"]

@require_GET
def parse(request):
    """
    This is an AJAX utility to get the needed context variables given a
    template name
    """
    form = ParseForm(request.GET)
    if form.is_valid():
        template_name = form.cleaned_data['template']
        try:
            template = loader.get_template(template_name)
        except TemplateDoesNotExist:
            return HttpResponse(json.dumps({"error": u"Could not load template '%s'" % template_name}), mimetype="application/json")
        tree = []
        for path in get_context(template):
            _extend(tree, path)
        return HttpResponse(json.dumps(tree), mimetype="application/json")
    else:
        return HttpResponse(json.dumps({"error": unicode(form.errors)}), mimetype="application/json")

def preview(request):
    """
    This is the view where the user can select rendering parameters (i.e.
    template+context)
    """
    form = RenderForm()
    ctx = {
        "form": form,
        "parse_url": reverse(parse),
        "render_url": reverse(render),
    }
    return TemplateResponse(
        request,
        "template_previewer/preview.html",
        ctx
    )

