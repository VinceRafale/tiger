from django import forms

from tiger.content.models import Content, PdfMenu, ItemImage


class ContentForm(forms.ModelForm):
    class Meta:
        model = Content
        exclude = ['site']


class PdfMenuForm(forms.ModelForm):
    content = forms.ChoiceField(choices=PdfMenu.CONTENT_CHOICES, widget=forms.RadioSelect)
    class Meta:
        model = PdfMenu
        exclude = ['site', 'page_count', 'featured']


class AddImageForm(forms.ModelForm):
    class Meta:
        model = ItemImage
        exclude = ['site']


class EditImageForm(forms.ModelForm):
    class Meta:
        model = ItemImage
        fields = ['title']
