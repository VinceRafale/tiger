import hashlib
from datetime import time

from django import forms
from django.contrib.auth.models import User

from tiger.accounts.models import Subscriber, ScheduledUpdate


class SubscriberForm(forms.ModelForm):
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField(required=False)

    class Meta:
        model = Subscriber
        exclude = ['user', 'site', 'send_updates']

    def __init__(self, data=None, files=None, *args, **kwargs):
        super(SubscriberForm, self).__init__(data, files, *args, **kwargs)
        if 'instance' in kwargs:
            user = kwargs['instance'].user
            self.initial.update({
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email
            })
            

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

    def save(self, commit=True):
        try:
            user = self.instance.user
        except User.DoesNotExist:
            user = User()
        for attr in ('first_name', 'last_name', 'email'):
            setattr(user, attr, self.cleaned_data[attr])
        if not user.username:
            user.username = hashlib.md5(''.join(str(v) for v in self.cleaned_data.values())).hexdigest() 
        user.save()
        self.instance.user = user
        if commit:
            self.instance.save()
        return self.instance


class AmPmTimeWidget(forms.widgets.Input):
    input_type = 'text'

    def render(self, name, value, attrs=None):
        value = value.strftime('%I:%M %p')
        return super(AmPmTimeWidget, self).render(name, value, attrs)
        
            
class AmPmTimeField(forms.Field):
    widget = AmPmTimeWidget

    def to_python(self, value):
        t, meridian = value.split()
        h, m = [int(v) for v in t.split(':')]
        if meridian == 'PM' and h != 12:
            h += 12
        elif meridian == 'AM' and h == 12:
            h = 0
        return time(h, m)
        

class ScheduledUpdateForm(forms.ModelForm):
    start_time = AmPmTimeField()

    class Meta:
        model = ScheduledUpdate
        exclude = ['site']
