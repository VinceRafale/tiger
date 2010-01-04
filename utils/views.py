from django.http import HttpResponseNotFound, HttpResponseServerError
from django.template import loader, RequestContext

from tiger.utils.template import load_custom


def render_custom(request, template, context):
    t = load_custom(request, template)
    c = RequestContext(request, context)
    return t.render(c)
    
def handler404(request):
    t = render_custom(request, '404.html')
    return HttpResponseNotFound(t)

def handler500(request):
    t = render_custom(request, '500.html')
    return HttpResponseServerError(t)
