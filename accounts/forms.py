import hashlib
from datetime import time

from django import forms
from django.contrib.auth.models import User

from tiger.accounts.models import Subscriber, ScheduledUpdate


class SubscriberForm(forms.ModelForm):
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    email = forms.EmailField(required=False)

    class Meta:
        model = Subscriber
        exclude = ['user', 'site', 'send_updates']

    def __init__(self, data=None, files=None, *args, **kwargs):
        super(SubscriberForm, self).__init__(data, files, *args, **kwargs)
        if kwargs.get('instance'):
            user = kwargs['instance'].user
            self.initial.update({
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email
            })
            

    def clean(self):
        super(SubscriberForm, self).clean()
        cleaned_data = self.cleaned_data
        update_via = cleaned_data['update_via']
        if update_via == Subscriber.VIA_EMAIL and not cleaned_data.get('email'):
            msg = "You must enter an e-mail address to use e-mail updates."
            raise forms.ValidationError(msg)
        if update_via == Subscriber.VIA_FAX and not cleaned_data.get('fax'):
            msg = "You must enter a fax number to use fax updates."
            raise forms.ValidationError(msg)
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')
        organization = cleaned_data.get('organization')
        if not ((first_name and last_name) or organization):
            raise forms.ValidationError('You must enter either an organization or a first and last name.')
        return cleaned_data

    def save(self, commit=True):
        subscriber = super(SubscriberForm, self).save(commit=False)
        try:
            user = subscriber.user
        except User.DoesNotExist:
            user = User()
        for attr in ('first_name', 'last_name', 'email'):
            setattr(user, attr, self.cleaned_data[attr])
        if not user.username:
            user.username = hashlib.md5(''.join(str(v) for v in self.cleaned_data.values())).hexdigest()[:30] 
        user.save()
        subscriber.user = user
        if commit:
            subscriber.save()
        return subscriber


class AmPmTimeWidget(forms.widgets.Input):
    input_type = 'text'

    def render(self, name, value, attrs=None):
        if value:
            value = value.strftime('%I:%M %p')
        else:
            value = ''
        return super(AmPmTimeWidget, self).render(name, value, attrs)
        
            
class AmPmTimeField(forms.Field):
    widget = AmPmTimeWidget
        

class ScheduledUpdateForm(forms.ModelForm):
    start_time = AmPmTimeField()

    class Meta:
        model = ScheduledUpdate
        exclude = ['site']

    # move this into form field later
    def clean_start_time(self):
        value = self.cleaned_data['start_time']
        t, meridian = value.split()
        h, m = [int(v) for v in t.split(':')]
        if meridian == 'PM' and h != 12:
            h += 12
        elif meridian == 'AM' and h == 12:
            h = 0
        return time(h, m)

