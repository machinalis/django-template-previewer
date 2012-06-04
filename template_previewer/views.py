import json

from django.http import HttpResponse, HttpResponseBadRequest
from django.template.response import TemplateResponse
from django.core.urlresolvers import reverse
from django.template import Template, Context, loader

from template_previewer.forms import RenderForm, ParseForm
from template_previewer.template_parser.context import get_context

def render(request):
    """This is the actually preview, rendered on an <iframe>"""
    if request.method != "POST":
        return HttpResponseBadRequest()
    form = RenderForm(request.POST)
    if form.is_valid():
        template_name = form.cleaned_data['template']
        template = loader.get_template(template_name)
        context = json.loads(form.cleaned_data['context'])
        c = Context(context)
        print template, c
        return HttpResponse(template.render(c))
    else:
        return HttpResponseBadRequest()


def parse(request):
    """
    This is an AJAX utility to get the needed context variables given a
    template name
    """
    if request.method != "POST":
        return HttpResponseBadRequest()
    form = ParseForm(request.POST)
    if form.is_valid():
        template_name = form.cleaned_data['template']
        template = Template(template_name)
        c = get_context(template)
        return HttpResponse(json.dumps(c))
    else:
        return HttpResponseBadRequest()


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

