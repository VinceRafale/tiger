from django.template import RequestContext

from tiger.utils.template import custom_load


def render_custom(request, template, context):
    t = custom_load(request, template)
    c = RequestContext(request, context)
    t.render(c)
    
    
