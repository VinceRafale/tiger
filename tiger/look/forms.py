from django import forms
from django.template import Template
from django.template.loader_tags import BlockNode

from lxml.html import fragments_fromstring, tostring
from lxml.html.clean import clean_html

from tiger.look.constants import TEMPLATE_TAG_ESCAPES, REQUIRED_BLOCKS
from tiger.look.models import *
from tiger.look.widgets import *

def get_skin_choices():
    return [(skin.url, skin.name) for skin in Skin.objects.all()]

class SkinSelectForm(forms.Form):
    skin = forms.ChoiceField(label='Theme', choices=get_skin_choices())


class HeaderFontForm(forms.ModelForm):
    header_font = forms.ModelChoiceField(queryset=FontFace.objects.all(), empty_label=None)
    header_color = forms.CharField(widget=ColorPickerWidget, required=False)

    class Meta:
        model = Skin
        fields = ('header_font', 'header_color',)
    
    def __init__(self, *args, **kwargs):
        """Ensures that the list of available FontFace objects is not cached,
        as ``forms.ModelChoiceField`` deliberately does.
        """
        super(HeaderFontForm, self).__init__(*args, **kwargs)
        self.fields['header_font'].queryset = FontFace.objects.all()


class BodyFontForm(forms.ModelForm):
    body_font = forms.ChoiceField(choices=FONT_CHOICES)
    body_color = forms.CharField(widget=ColorPickerWidget, required=False)

    class Meta:
        model = Skin
        fields = ('body_font', 'body_color',)
    

class BackgroundForm(forms.Form):
    bg = forms.ModelChoiceField(label='Preloaded backgrounds', queryset=Background.objects.all())
    
    def __init__(self, *args, **kwargs):
        """Ensures that the list of available images objects is not cached,
        as ``forms.ChoiceField`` deliberately does.
        """
        super(BackgroundForm, self).__init__(*args, **kwargs)
        self.fields['bg'].queryset = Background.objects.filter(site__isnull=True)


class BackgroundColorForm(forms.Form):
    background_color = forms.CharField(widget=ColorPickerWidget)


class CustomBackgroundForm(forms.ModelForm):
    class Meta:
        model = Background
        exclude = ('site', 'name', 'image', 'staged_image', 'color',)


class BackgroundImageForm(forms.ModelForm):
    class Meta:
        model = Background
        fields = ('staged_image',)


class LogoForm(forms.ModelForm):
    class Meta:
        model = Logo


class ColorForm(forms.ModelForm):
    masthead_color = forms.CharField(widget=ColorPickerWidget, required=False)
    masthead_font_color = forms.CharField(widget=ColorPickerWidget, required=False)
    menu_color = forms.CharField(widget=ColorPickerWidget, required=False)
    center_color = forms.CharField(widget=ColorPickerWidget, required=False)
    button_color = forms.CharField(widget=ColorPickerWidget, required=False)
    button_text_color = forms.CharField(widget=ColorPickerWidget, required=False)
    shaded_color = forms.CharField(label='Accent color', widget=ColorPickerWidget, required=False)

    class Meta:
        model = Skin
        fields = (
            'masthead_color',
            'masthead_font_color',
            'menu_color',
            'center_color',
            'button_color',
            'button_text_color',
            'shaded_color',
        )


pseudoblock_re = re.compile(r'\{\{([a-z]+)\}\}')

class HtmlForm(forms.Form):
    html = forms.CharField()

    def clean_html(self):
        elements = fragments_fromstring(self.cleaned_data['html'])
        html = ''.join(tostring(clean_html(element)) for element in elements)
        with_blocks = pseudoblock_re.sub(r'&& block \1 &&&& endblock &&', html)
        for bit, tag in TEMPLATE_TAG_ESCAPES:
            with_blocks = with_blocks.replace(bit, tag)    
        with_blocks = re.sub(r'&& block ([a-z]+) &&&& endblock &&', r'{% block \1 %}{% endblock %}', with_blocks)
        t = Template(with_blocks)
        required = list(REQUIRED_BLOCKS)
        invalid = []
        dups = []
        block_nodes = t.nodelist.get_nodes_by_type(BlockNode)
        for node in block_nodes:
            name = node.name
            if name in required:
                required.remove(name)
            else:
                if name in REQUIRED_BLOCKS:
                    dups.append(name)
                else:
                    invalid.append(name)
        if len(required):
            raise forms.ValidationError("You are missing the following blocks: %s" % ', '.join('<code>{{%s}}</code>' % r for r in required))
        if len(dups):
            raise forms.ValidationError("The following blocks appear more than once: %s" % ', '.join('<code>{{%s}}</code>' % d for d in dups))
        if len(invalid):
            raise forms.ValidationError("The following blocks are invalid: %s" % ', '.join('<code>{{%s}}</code>' % i for i in invalid))
        return with_blocks
