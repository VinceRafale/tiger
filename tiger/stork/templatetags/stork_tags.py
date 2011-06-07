from django import template
from django.forms.fields import CheckboxInput, FileField

from tiger.stork import Stork

register = template.Library()

@register.filter
def is_checkbox(value):
    return isinstance(value.field.widget, CheckboxInput)


@register.filter
def is_filefield(value):
    return isinstance(value.field, FileField)


@register.simple_tag
def build_css(theme):
    stork = Stork(theme)
    return ';\n'.join("$%s: rgba(%s,%s)" % (swatch.id, swatch.instance.color, swatch.instance.alpha) for swatch in stork.swatches) + ";"

