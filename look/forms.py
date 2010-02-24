from django import forms

from tiger.look.models import *

def get_skin_choices():
    return [(skin.url, skin.name) for skin in Skin.objects.all()]

class SkinSelectForm(forms.Form):
    skin = forms.ChoiceField(label='Theme', choices=get_skin_choices())
