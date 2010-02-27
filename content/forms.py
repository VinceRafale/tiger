from django import forms

from tiger.content.models import Content, PdfMenu


class ContentForm(forms.ModelForm):
    class Meta:
        model = Content
        exclude = ['image', 'site']


class PdfMenuForm(forms.ModelForm):
    content = forms.ChoiceField(choices=PdfMenu.CONTENT_CHOICES, widget=forms.RadioSelect)
    class Meta:
        model = PdfMenu
        exclude = ['site', 'page_count', 'featured']
