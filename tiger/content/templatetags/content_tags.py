from django import template
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.template.defaultfilters import linebreaks
from django.utils.safestring import mark_safe

from tiger.content.models import Content

register = template.Library()

def get_content(site, slug):
    """Checks the cache for the current content item, retrieves it if
    possible, and retrieves from database and adds to cache if not.  
    """
    cache_key = '%d-%s' % (site.id, slug)
    content = cache.get(cache_key)
    if content is None:
        content = Content.objects.get(site=site, slug=slug)
        cache.set(cache_key, content)
    return content

@register.simple_tag
def get_title(site, slug):
    return get_content(site=site, slug=slug).title
    
@register.simple_tag
def get_body(site, slug):
    return linebreaks(get_content(site=site, slug=slug).text)
    
@register.simple_tag
def get_image(site, slug, size):
    c = get_content(site=site, slug=slug)
    try:
        img = c.image
    except ObjectDoesNotExist:
        return ''
    if img is None:
        return ''
    img_size = getattr(img, size)
    return mark_safe('<a href="%s"><img class="inset-left" src="%s" /></a>' % (img.get_absolute_url(), img_size.url))
