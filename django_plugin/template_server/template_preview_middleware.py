import json

from django.http import HttpResponse
from django.conf import settings
from django.contrib.staticfiles import views
from django.template import Template, Context

from template_parser.context import get_context

class TemplatePreviewMiddleware(object):

    def process_request(self, request):
        if request.path.startswith(settings.STATIC_URL):
            static_path = request.path[len(settings.STATIC_URL):]
            return views.serve(request, static_path)
        else:
            if request.method == 'POST':
                template_str = request.POST.get('template', 'no template provided')
                template = Template(template_str)
                if 'context' in request.POST:
                    context = json.loads(request.POST['context'])
                    c = Context(context)
                    return HttpResponse(template.render(c))
                else:
                    c = get_context(template)
                    return HttpResponse(json.dumps(c))
            else:
                return HttpResponse(
                """
                    <form action="." method="post">
                        Template: <input type="text" name="template"><br/>
                        Data: <textarea name="context"></textarea><br/>
                        <input type="submit">
                    </form>
                """)
