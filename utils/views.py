from django.http import HttpResponseNotFound, HttpResponseServerError
from django.template import loader, RequestContext

from tiger.utils.template import custom_load


def render_custom(request, template, context):
    t = custom_load(request, template)
    c = RequestContext(request, context)
    t.render(c)
    return t
    
def handler404(request):
    t = render_custom(request, '404.html')
    return HttpResponseNotFound(t)

def handler500(request):
    t = render_custom(request, '500.html')
    return HttpResponseServerError(t)
