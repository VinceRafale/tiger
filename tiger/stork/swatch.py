from component import BaseComponent
from errors import StorkConfigurationError
from widgets import ColorPickerWidget

from django import forms
from django.utils import simplejson as json

from tiger.stork.models import Swatch
from tiger.stork.widgets import ColorPickerWidget


class SwatchComponent(BaseComponent):
    model = Swatch

    def __init__(self, panel, group, name, order, default=None, properties=None):
        if default is None:
            raise StorkConfigurationError('"default" is required for swatch components')
        if properties is None or len(properties) == 0:
            raise StorkConfigurationError('swatches must contain at least one property')
        super(SwatchComponent, self).__init__(panel, group, name, order)
        self.default = default
        self.properties = [Property(**p) for p in properties]

    def get_picker_id(self):
        return '#picker-%s-color' % self.key
    
    def get_hidden_input_id(self):
        return '#id_%s-color' % self.key

    def get_selector_prop(self):
        return [
            '%s{%s:#' % (prop.selector, prop.css_property) 
            for prop in self.properties
        ]

    def get_style_tag_contents(self):
        selectors = ''.join([
            '%s%s;}' % (prop, self.instance.color) 
            for prop in self.get_selector_prop()
        ])
        return selectors

    def for_json(self):
        return [
            self.get_picker_id(),
            "#" + self.style_tag_id,
            self.get_hidden_input_id(),
            self.get_selector_prop()
        ]

    def get_defaults(self):
        return {'color': self.default}

    def get_formfield_overrides(self):
        return {
            'color': forms.CharField(
                label=self.name,
                widget=ColorPickerWidget, 
                required=False
            )
        }


class Property(object):
    def __init__(self, selector, css_property):
        self.selector = selector 
        self.css_property = css_property  
