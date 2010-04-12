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


class MailChimpForm(forms.ModelForm):
    mailchimp_send_blast = forms.ChoiceField(
        label='Would you like Takeout Tiger to create MailChimp campaigns to accompany your marketing blasts?',
        widget=forms.RadioSelect, choices=Social.CAMPAIGN_CHOICES)

    class Meta:
        model = Social
        fields = ['mailchimp_allow_signup', 'mailchimp_send_blast']
