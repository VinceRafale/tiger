from django import forms

from tiger.utils.forms import BetterModelForm
from tiger.sms.models import Campaign, SmsSettings


class CampaignForm(BetterModelForm):
    body = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = Campaign
        fields = (
            'title',
            'body',
            'filter_on',
            'filter_value',
            'starred',
            'count',
        )


class SettingsForm(BetterModelForm):
    intro_sms = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = SmsSettings
        fields = (
            'send_intro',
            'intro_sms',
        )

    def clean(self):
        send_intro = self.cleaned_data.get('send_intro')
        intro_sms = self.cleaned_data.get('intro_sms')
        if send_intro and not intro_sms:
            raise forms.ValidationError('You must provide the text for the introductory SMS if you select "Send an automated introductory SMS".')
        return self.cleaned_data

