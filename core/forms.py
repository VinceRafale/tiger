from django import forms
from django.contrib.localflavor.us.forms import USPhoneNumberField

from tiger.core.models import *


def get_order_form(instance):
    """For a given ``instance`` of ``core.models.Item``, returns a form 
    appropriate for completing an order, with a quantity field for all forms,
    radio select for variant (if applicable), and checkboxes for substitutions/
    upgrades (if applicable).
    """
    variants = instance.variant_set.all()
    upgrades = instance.upgrade_set.all()
    attrs = {
        'quantity': forms.IntegerField(min_value=1, initial=1),
        'notes': forms.CharField(required=False)
    }
    if variants.count() > 1:
        max = variants.order_by('-price')[0].id
        attrs['variant'] = forms.ModelChoiceField(queryset=variants, widget=forms.RadioSelect, empty_label=None, initial=max)
    if upgrades.count():
        attrs['upgrades'] = forms.ModelMultipleChoiceField(queryset=upgrades, widget=forms.CheckboxSelectMultiple, required=False)
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


class OrderForm(forms.Form):
    name = forms.CharField()
    phone = USPhoneNumberField()
    pickup = forms.CharField(label='Time you will pick up your order')
