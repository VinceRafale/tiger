from django import forms
from haystack.forms import SearchForm


class MenuSearchForm(SearchForm):
    vegetarian = forms.BooleanField(label='Only vegetarian', required=False)
    spicy = forms.BooleanField(label='Only spicy', required=False)

    def search(self):
        sqs = super(MenuSearchForm, self).search()
        if self.cleaned_data['vegetarian']:
            sqs = sqs.filter(vegetarian=True)
        if self.cleaned_data['spicy']:
            sqs = sqs.filter(spicy=True)
        return sqs
