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
