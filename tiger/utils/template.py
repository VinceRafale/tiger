from django.core.cache import cache
from django.template import Template
from django.template.loader import find_template_source, get_template_from_string, get_template


def load_custom(request, template_name):
    """Fakes a template loader that pulls from a custom template directory for 
    the current ``Site``.  This currently can't be done with an additional real 
    template loader because there is no way to feed it the domain at runtime.
    """
    try:
        source, origin = find_template_source(template_name, [request.site.subdomain])
    except:
        template = get_template(template_name)
    else:
        template = get_template_from_string(source, origin, template_name)
    return template
        
