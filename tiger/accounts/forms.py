import hashlib
from datetime import time

from pycheddar import *

from django import forms
from django.contrib.auth.models import User

from tiger.accounts.models import Account, Subscriber, Site, TimeSlot


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
        if type(value) == time:
            value = value.strftime('%I:%M %p')
        return super(AmPmTimeWidget, self).render(name, value, attrs)
        
            
class AmPmTimeField(forms.Field):
    widget = AmPmTimeWidget
        
    def clean(self, value):
        if value:
            t, meridian = value.split()
            h, m = [int(v) for v in t.split(':')]
            if meridian == 'PM' and h != 12:
                h += 12
            elif meridian == 'AM' and h == 12:
                h = 0
            return time(h, m)
        return None


class LocationForm(forms.ModelForm):
    class Meta:
        model = Site
        fields = ['street', 'city', 'state', 'zip', 'phone', 'fax_number', 'timezone']


class TimeSlotForm(forms.ModelForm):
    start = AmPmTimeField(label='Open', required=False)
    stop = AmPmTimeField(label='Close', required=False)

    class Meta:
        model = TimeSlot
        fields = ['start', 'stop']

    def clean(self):
        super(TimeSlotForm, self).clean()
        cleaned_data = self.cleaned_data
        if all(cleaned_data.values()):
            self.noop = False
            return cleaned_data
        if not any(cleaned_data.values()):
            self.noop = True
            return cleaned_data
        raise forms.ValidationError('You must specify an opening and closing time.')

    def save(self, commit=False):
        if self.noop:
            return
        return super(TimeSlotForm, self).save(commit)
        

class SignupForm(forms.ModelForm):
    subdomain = forms.CharField()
    first_name = forms.CharField()
    last_name = forms.CharField()
    user_email = forms.EmailField(label='E-mail address')
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm password', widget=forms.PasswordInput)
    cc_number = forms.CharField()
    cc_expiration = forms.CharField()

    class Meta:
        model = Account
        exclude = ['user', 'auth_net_api_key', 'auth_net_api_login']

    def clean_subdomain(self):
        """Validate that the email is not already in use.
        """
        try:
            user = Site.objects.get(domain__iexact=self.cleaned_data['subdomain'])
        except Site.DoesNotExist:
            return self.cleaned_data['subdomain']
        raise forms.ValidationError("A user with that e-mail address already exists.")

    def clean(self):
        """Verify that the values entered into the two password fields
        match. Note that an error here will end up in
        ``non_field_errors()`` because it doesn't apply to a single
        field.
        """
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError("The two password fields didn't match.")
        self.process_cc()
        return self.cleaned_data

    def process_cc(self):
        cleaned_data = self.cleaned_data
        CheddarGetter.auth('jonathan@threadsafelabs.com', 'p1nnoch1o')
        CheddarGetter.set_product_code('product code')
        customer = Customer()
        customer.first_name = cleaned_data.get('first_name')
        customer.last_name = cleaned_data.get('last_name')
        customer.email = cleaned_data.get('email') or cleaned_data.get('user_email')
        sub = Subscription()
        sub.plan_code = 'BASIC'
        sub.cc_first_name = cleaned_data.get('first_name')
        sub.cc_last_name = cleaned_data.get('last_name')
        sub.cc_zip = cleaned_data.get('zip')
        sub.cc_number = cleaned_data.get('cc_number')
        sub.cc_expiration = cleaned_data.get('cc_expiration')
        customer.subscription = sub
        try:
            customer.save()
        except GatewayFailure:
            raise forms.ValidationError('We were unable to process your credit card.')
        except MouseTrap:
            raise forms.ValidationError('Error connecting to payment server.  Please try again.')
        # what does this object really return?
        self.customer = customer

    def save(self):
        instance = super(SignupForm, self).save(commit=False)
        cleaned_data = self.cleaned_data
        first_name = cleaned_data['first_name']
        last_name = cleaned_data['last_name']
        email = cleaned_data['user_email']
        password = cleaned_data['password']
        user = User(
            username=hashlib.md5(REPLACE_ME).hexdigest(), 
            first_name=first_name, 
            last_name=last_name,
            email=email
        )
        user.set_password(password)
        user.save()
        instance.user = user
        instance.save()
        site = Site()
        for k in ('street', 'city', 'state', 'zip', 'phone',):
            setattr(site, getattr(instance, k))
        site.domain = cleaned_data['subdomain']
        site.fax_number = instance.fax
        site.name = instance.company_name
        site.save()


class DomainForm(forms.ModelForm):
    class Meta:
        model = Site
        fields = ('domain',)
