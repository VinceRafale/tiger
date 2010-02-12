from django import forms

from tiger.notify.models import Social


class TwitterForm(forms.ModelForm):
    class Meta:
        model = Social
        fields = ['twitter_screen_name']
