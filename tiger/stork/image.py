from component import BaseComponent
from errors import StorkConfigurationError

from django import forms
from django.core.files.base import ContentFile
from django.template.loader import render_to_string

from tiger.stork.models import Image


class ImageComponent(BaseComponent):
    model = Image
    css_template = """%s {
        background-image: url('%s');
        background-repeat: %s;
        text-indent:%s;
    }
    """

    def __init__(self, panel, group, name, order, selector=None, text_indent=True, allow_tiling=False, **kwargs):
        if selector is None:
            raise StorkConfigurationError('"selector" is required for image components')
        super(ImageComponent, self).__init__(panel, group, name, order, **kwargs)
        self.selector = selector
        self.text_indent = text_indent
        self.allow_tiling = allow_tiling

    def get_style_tag_contents(self):
        return self.get_css()

    def get_css(self, tiling=False):
        instance = self.instance
        image = instance.staged_image or instance.image
        if not image:
            return ''
        return self.css_template % (
            self.selector, 
            image.url, 
            'repeat' if (instance.tiling or tiling) else 'no-repeat',
            '-9999px' if self.text_indent else 'default'
        )

    def get_defaults(self):
        return {
            'staged_image': None,
            'image': None,
            'tiling': False
        }

    def formfield_excludes(self):
        if self.allow_tiling:
            return ['image']
        return ['image', 'tiling']

    def save(self, data=None, files=None):
        instance = self.instance
        if data:
            if data.has_key('%s-stale' % self.id):
                instance.staged_image.delete()
            elif bool(instance.staged_image):
                instance.image.save(
                    instance.staged_image.name.split('/')[-1], 
                    ContentFile(instance.staged_image.file.file.read()))
                instance.staged_image.delete()
            if data.has_key('%s-delete' % self.id):
                instance.image.delete()
            instance.tiling = data.get('%s-tiling' % self.id) == 'on'
            instance.save()
        else:
            super(ImageComponent, self).save(data, files)
