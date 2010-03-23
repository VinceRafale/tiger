from django import template
from django.core.exceptions import ObjectDoesNotExist
from django.template.defaultfilters import linebreaks
from django.utils.safestring import mark_safe

from tiger.content.models import Content

register = template.Library()


@register.simple_tag
def get_title(site, slug):
    return Content.objects.get(site=site, slug=slug).title
    
@register.simple_tag
def get_body(site, slug):
    return linebreaks(Content.objects.get(site=site, slug=slug).text)
    
@register.simple_tag
def get_image(site, slug, size):
    c = Content.objects.get(site=site, slug=slug)
    try:
        img = c.image
    except ObjectDoesNotExist:
        return ''
    if img is None:
        return ''
    img_size = getattr(img, size)
    return mark_safe('<a href="%s"><img class="inset-left" src="%s" /></a>' % (img.get_absolute_url(), img_size.url))
