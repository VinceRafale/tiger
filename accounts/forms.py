from django import forms
from django.contrib.auth.models import User

from tiger.accounts.models import Subscriber


class SubscriberForm(forms.ModelForm):
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField(required=False)

    class Meta:
        model = Subscriber
        exclude = ['user', 'site']

    def clean(self):
        super(SubscriberForm, self).clean()
        cleaned_data = self.cleaned_data
        send_updates = cleaned_data.get('send_updates')
        if not send_updates:
            return cleaned_data
        update_via = cleaned_data['update_via']
        if update_via == Subscriber.VIA_EMAIL and not cleaned_data.get('email'):
            msg = "You must enter an e-mail address to use e-mail updates."
            raise forms.ValidationError(msg)
        if update_via == Subscriber.VIA_FAX and not cleaned_data.get('fax'):
            msg = "You must enter a fax number to use fax updates."
            raise forms.ValidationError(msg)
        return cleaned_data
            
