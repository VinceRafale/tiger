from django import template
from django.template.defaultfilters import linebreaks

from tiger.content.models import Content

register = template.Library()


@register.simple_tag
def get_title(site, slug):
    return Content.objects.get(site=site, slug=slug).title
    
@register.simple_tag
def get_body(site, slug):
    return linebreaks(Content.objects.get(site=site, slug=slug).text)
