from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple

from tiger.accounts.models import Subscriber
from tiger.notify.models import Social, Blast


class TwitterForm(forms.ModelForm):
    class Meta:
        model = Social
        fields = ['twitter_screen_name']


class BlastForm(forms.ModelForm):
    subscribers = forms.ModelMultipleChoiceField(queryset=Subscriber.objects.all(), widget=FilteredSelectMultiple('subscribers', False))

    class Meta:
        model = Blast
        fields = ['name', 'pdf', 'subscribers']
