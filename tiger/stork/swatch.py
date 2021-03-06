from component import BaseComponent
from errors import StorkConfigurationError
from widgets import ColorPickerWidget

from django import forms
from django.utils import simplejson as json

from tiger.stork.models import Swatch
from tiger.stork.widgets import ColorPickerWidget


class SwatchComponent(BaseComponent):
    model = Swatch

    def __init__(self, panel, group, name, order, default=None, properties=None, **kwargs):
        if default is None:
            raise StorkConfigurationError('"default" is required for swatch components')
        if properties is None or len(properties) == 0:
            raise StorkConfigurationError('swatches must contain at least one property')
        super(SwatchComponent, self).__init__(panel, group, name, order, **kwargs)
        self.default = default
        self.properties = [Property(**p) for p in properties]

    def get_picker_id(self):
        return '#picker-%s-color' % self.id
    
    def get_hidden_input_id(self):
        return '#id_%s-color' % self.id

    def get_selector_prop(self):
        selector_property = """%(selector)s {
            %(property)s: rgb(%%(triplet)s);
            %(property)s: rgba(%%(triplet)s,%%(alpha)s);
        }
        %(ie_selector)s {
            %(property)s: %%(ie_color)s;
        }
        """
        return [
            selector_property % {
                'selector': prop.selector, 
                'property': prop.css_property,
                'ie_selector': ','.join([
                    '.ie6 %s, .ie7 %s' % (select, select) 
                    for select in prop.selector.split(',')
                ])
            }
            for prop in self.properties
        ]

    def get_style_tag_contents(self):
        instance = self.instance
        selectors = ''.join([
            prop % {
                'triplet': instance.color, 
                'alpha': instance.alpha,
                'ie_color': ("transparent" if instance.alpha == 0 else "rgb(%s)" % instance.color)
            }
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
        return {'color': self.default, 'alpha': '1.0'}

    def get_formfield_overrides(self):
        return {
            'color': forms.CharField(
                label=self.name,
                widget=ColorPickerWidget, 
                required=False
            ),
            'alpha': forms.CharField(
                widget=forms.HiddenInput 
            )
        }


class Property(object):
    def __init__(self, selector, css_property):
        self.selector = selector 
        self.css_property = css_property  
