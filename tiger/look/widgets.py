from django import forms
from django.utils.safestring import mark_safe

class ColorPickerWidget(forms.TextInput):
    input_type = 'hidden'
    is_hidden = False

    class Media:
        css = {
            'screen': ('swatch.css',)
        }


    def render(self, name, value, attrs=None):
        hidden_input = super(ColorPickerWidget, self).render(name, value, attrs)
        color_picker = """<div class="picker-widget" id="picker-%s">
            <div style="background-color:#%s;"></div></div>""" % (name, value or 'ffffff')
        return mark_safe(hidden_input + color_picker)
