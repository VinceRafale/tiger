from django import forms

from tiger.utils.forms import BetterModelForm
from tiger.sales.exceptions import CapExceeded
from tiger.sms.models import Campaign, SmsSettings
from tiger.sms.sender import Sender


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

    def __init__(self, data=None, site=None, *args, **kwargs):
        super(CampaignForm, self).__init__(data, *args, **kwargs)
        if len(site.sms.keywords) > 1:
            self.fields['keyword'] = forms.ChoiceField(label='Subscriber list', choices=[(l, l) for l in site.sms.keywords])
        self.site = site

    def clean(self):
        data = self.cleaned_data
        count = self.cleaned_data.get('count')
        sender = Sender(self.site, data.get('body', ''))
        try:
            sender.add_recipients(*['dummy' for n in range(count)])
        except CapExceeded, e:
            if e.cap_type == 'soft':
                self.cap_exceeded = True
            else:
                raise forms.ValidationError('The send count requested will exceed your monthly plan limit.')
        return data


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

