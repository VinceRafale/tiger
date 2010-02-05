from django import forms

from tiger.content.models import Content


class ContentForm(forms.ModelForm):
    class Meta:
        model = Content
        exclude = ['image', 'site']
