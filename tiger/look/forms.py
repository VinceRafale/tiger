from django import forms

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
        self.fields['bg'].queryset = Background.objects.all()


class BackgroundColorForm(forms.Form):
    background_color = forms.CharField(widget=ColorPickerWidget)


class CustomBackgroundForm(forms.ModelForm):
    class Meta:
        model = Background
        exclude = ('site', 'name', 'image', 'color',)


class BackgroundImageForm(forms.ModelForm):
    class Meta:
        model = Background
        fields = ('image',)


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
    

class LogoForm(forms.Form):
    class Meta:
        model = Skin
        fields = ('logo',)
