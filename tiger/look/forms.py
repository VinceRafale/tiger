from django import forms

from tiger.look.models import *

def get_skin_choices():
    return [(skin.url, skin.name) for skin in Skin.objects.all()]

class SkinSelectForm(forms.Form):
    skin = forms.ChoiceField(label='Theme', choices=get_skin_choices())


class HeaderFontForm(forms.Form):
    header_font = forms.ModelChoiceField(queryset=FontFace.objects.all())
    
    def __init__(self, *args, **kwargs):
        """Ensures that the list of available FontFace objects is not cached,
        as ``forms.ModelChoiceField`` deliberately does.
        """
        super(HeaderFontForm, self).__init__(*args, **kwargs)
        self.fields['header_font'].queryset = FontFace.objects.all()


class BodyFontForm(forms.Form):
    body_font = forms.ChoiceField(choices=FONT_CHOICES)


class BackgroundForm(forms.Form):
    bg = forms.ModelChoiceField(label='Preloaded backgrounds', queryset=Background.objects.all())
    
    def __init__(self, *args, **kwargs):
        """Ensures that the list of available images objects is not cached,
        as ``forms.ChoiceField`` deliberately does.
        """
        super(BackgroundForm, self).__init__(*args, **kwargs)
        self.fields['bg'].queryset = Background.objects.all()


class BackgroundColorForm(forms.Form):
    background_color = forms.CharField()


class CustomBackgroundForm(forms.ModelForm):
    class Meta:
        model = Background
        exclude = ('name', 'image', 'color',)


class BackgroundImageForm(forms.ModelForm):
    class Meta:
        model = Background
        fields = ('image',)
