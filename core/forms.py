from django import forms

from tiger.core.models import *


def get_order_form(instance, variants, upgrades):
    """For a given ``instance`` of ``core.models.Item``, returns a form 
    appropriate for completing an order, with a quantity field for all forms,
    radio select for variant (if applicable), and checkboxes for substitutions/
    upgrades (if applicable).
    """
    attrs = {
        'quantity': forms.IntegerField(min_value=1, initial=1)
    }
    if variants.count() > 1:
        attrs['variant'] = forms.ModelChoiceField(queryset=variants, widget=forms.RadioSelect, empty_label=None)
    if upgrades.count():
        attrs['upgrades'] = forms.ModelMultipleChoiceField(queryset=upgrades, widget=forms.CheckboxSelectMultiple)
    return type('OrderForm', (forms.Form,), attrs)


class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        exclude = ['site']


def get_item_form(site):
    class ItemForm(forms.ModelForm):
        section = forms.ModelChoiceField(queryset=site.section_set.all())
        class Meta:
            model = Item
            exclude = ['site', 'image']
    return ItemForm



