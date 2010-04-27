from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple

from tiger.accounts.models import Subscriber
from tiger.notify.models import Social, Release
from tiger.utils.widgets import MarkItUpWidget


class TwitterForm(forms.ModelForm):
    class Meta:
        model = Social
        fields = ['twitter_screen_name']


class MailChimpForm(forms.ModelForm):
    mailchimp_send_blast = forms.ChoiceField(
        label='Would you like Takeout Tiger to create MailChimp campaigns to accompany your marketing blasts?',
        widget=forms.RadioSelect, choices=Social.CAMPAIGN_CHOICES)

    class Meta:
        model = Social
        fields = ['mailchimp_allow_signup', 'mailchimp_send_blast']


class PublishForm(forms.ModelForm):
    body = forms.CharField(widget=MarkItUpWidget)

    class Meta:
        model = Release
        exclude = ('site',)
