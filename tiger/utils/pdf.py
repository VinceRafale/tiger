import os.path
from django.conf import settings
from django.template.loader import get_template
from django.template import Context
import ho.pisa as pisa
import cStringIO as StringIO


def fetch_resources(uri, rel):
    path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ''))
    return path

def render_to_pdf(template_name, context_dict):
    template = get_template(template_name)
    context_dict.update({'MEDIA_URL': settings.MEDIA_URL})
    context = Context(context_dict)
    html  = template.render(context)
    result = StringIO.StringIO()
    pdf = pisa.pisaDocument(StringIO.StringIO(html.encode("UTF-8")), result, link_callback=fetch_resources)
    return result.getvalue()

