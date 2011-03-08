from django import forms
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe

from tiger.content.models import ItemImage


class ImageChooserWidget(forms.HiddenInput):
    class Media:
        css = {
            'screen': (
                'css/jquery.fancybox-1.3.0.css',
            )
        }
        js = (
            'js/jquery.fancybox-1.3.0.pack.js',
            'js/chooser.js',
        )

    def __init__(self, attrs=None, site=None):
        super(ImageChooserWidget, self).__init__(attrs=attrs)
        self.images = site.itemimage_set.all()

    def render(self, name, value, attrs=None):
        html = super(ImageChooserWidget, self).render(name, value, {'class': 'chooser-input'}) 
        html = '<div class="img-chooser-wrap">' + html
        if value:
            html += '<img src="%s" />' % ItemImage.objects.get(id=value).thumb.url
        else:
            html += '<img src="%s" />' % '/static/img/blank.jpg'
        anchor = ' <p><a href="%s" class="chooser">%s</a> ' % (
            reverse('dashboard_get_images'),
            'Change' if value else 'Add'
        )
        if value:
            anchor += '<a href="#" class="chooser-remove">Remove</a>'
        html += anchor
        html += '</p></div>'
        return mark_safe(html)
