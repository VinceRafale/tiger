from django import template
from django.forms.fields import CheckboxInput, FileField

register = template.Library()

@register.filter
def is_checkbox(value):
    return isinstance(value.field.widget, CheckboxInput)


@register.filter
def is_filefield(value):
    return isinstance(value.field, FileField)
