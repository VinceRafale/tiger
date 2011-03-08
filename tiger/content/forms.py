from django import forms

from tiger.content.models import Content, PdfMenu, ItemImage
from tiger.dashboard.widgets import ImageChooserWidget
from tiger.utils.forms import BetterModelForm


class ContentForm(BetterModelForm):
    class Meta:
        model = Content
        exclude = ['site']

    def __init__(self, data=None, site=None, *args, **kwargs):
        super(ContentForm, self).__init__(data, *args, **kwargs)
        self.fields['image'].widget = ImageChooserWidget(site=site)
        self.fields['showcase'].widget = ImageChooserWidget(site=site)


class PdfMenuForm(BetterModelForm):
    class Meta:
        model = PdfMenu
        exclude = ['site', 'page_count', 'featured']

    def __init__(self, data=None, site=None, *args, **kwargs):
        super(PdfMenuForm, self).__init__(data=data, *args, **kwargs)
        self.site = site
        self.fields['sections'].queryset = site.section_set.all()


class AddImageForm(BetterModelForm):
    class Meta:
        model = ItemImage
        exclude = ['site']


class EditImageForm(BetterModelForm):
    class Meta:
        model = ItemImage
        fields = ['title', 'description']
