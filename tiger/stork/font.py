from component import BaseComponent
from errors import StorkConfigurationError
from font_choices import WebFonts

from django import forms
from django.template.loader import render_to_string

from tiger.stork.models import Font, FontStack



class FontComponent(BaseComponent):
    model = Font

    def __init__(self, panel, group, name, order, selector=None, default=None, fontface=False, **kwargs):
        if selector is None:
            raise StorkConfigurationError('"selector" is required for font components')
        if default is None:
            raise StorkConfigurationError('"default" is required for font components')
        try:
            self.default = getattr(WebFonts, default)
        except:
            raise StorkConfigurationError('Font component defaults must be one of: ARIAL, GARAMOND, GEORGIA, IMPACT, MONOSPACE, TIMES, TREBUCHET, VERDANA')
        super(FontComponent, self).__init__(panel, group, name, order, **kwargs)
        self.selector = selector
        self.fontface = fontface

    def get_style_tag_contents(self):
        return self.get_css()

    def get_css(self, font=None):
        return render_to_string('stork/font.css', {'component': self, 'ff': font or self.instance.font})

    def get_mobile_css(self, font=None):
        return render_to_string('stork/mobile-font.css', {'component': self, 'ff': font or self.instance.font})

    def webfont(self):
        return self.get_value(self.id)

    def get_defaults(self):
        return {
            'font': FontStack.objects.get(
                        ttf='', 
                        stack=self.default
                    ).id
        }

    def for_json(self):
        return {
            'allowFontface': self.fontface,
            'selector': '#id_%s-font' % self.id,
            'styleTagId': '#' + self.style_tag_id,
            'link': reverse('font_css', args=[self.id]).rstrip('.css')
        }

    def get_formfield_overrides(self):
        return {
            'font': forms.ModelChoiceField(
                label=self.name,
                empty_label=None,
                queryset=FontStack.objects.all()
            )
        }
