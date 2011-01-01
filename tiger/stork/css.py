from component import BaseComponent
from errors import StorkConfigurationError

from django import forms
from django.template.loader import render_to_string

from tiger.stork.models import CSS


class CssComponent(BaseComponent):
    model = CSS

    def __init__(self, panel, group, name, order, default=None):
        super(CssComponent, self).__init__(panel, group, name, order)
        self.default = default

    def get_style_tag_contents(self, staged=False):
        return self.instance.css

    def get_defaults(self):
        return {
            'css': self.default
        }
