import hashlib
from datetime import time, date

from pychargify.api import *

from django import forms
from django.conf import settings
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
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm password', widget=forms.PasswordInput)
    cc_number = forms.CharField(label='Card number')
    month = forms.CharField()
    year = forms.CharField()

    class Meta:
        model = Account
        fields = (
            'email',
            'zip',
        )

    def clean_email(self):
        """Validate that the e-mail is not already in use.
        """
        try:
            User.objects.get(email__iexact=self.cleaned_data['email'])
        except User.DoesNotExist:
            return self.cleaned_data['email']
        raise forms.ValidationError("That e-mail address is already in use.")

    def clean_subdomain(self):
        """Validate that the subdomain is not already in use.
        """
        try:
            Site.objects.get(domain__iexact=self.cleaned_data['subdomain'])
        except Site.DoesNotExist:
            return self.cleaned_data['subdomain']
        raise forms.ValidationError("That subdomain is already in use.")

    def clean_month(self):
        month = self.cleaned_data['month']
        msg = 'Please enter a valid month (00-12).'
        try:
            month = int(month)
        except ValueError:
            raise forms.ValidationError(msg)
        if 0 <= month <= 12:
            return month
        raise forms.ValidationError(msg)

    def clean_year(self):
        year = self.cleaned_data['year']
        current_year = date.today().year
        msg = 'Please enter a valid year (%d or later).' % current_year
        try:
            year = int(year)
        except ValueError:
            raise forms.ValidationError(msg)
        if year < current_year:
            raise forms.ValidationError(msg)
        return year

    def clean_password2(self):
        """Verify that the values entered into the two password fields
        match. Note that an error here will end up in
        ``non_field_errors()`` because it doesn't apply to a single
        field.
        """
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError("The two password fields didn't match.")

    def clean(self):
        if not self._errors:
            self.process_cc()
        return self.cleaned_data

    def process_cc(self):
        cleaned_data = self.cleaned_data
        chargify = Chargify(settings.CHARGIFY_API_KEY, settings.CHARGIFY_SUBDOMAIN)
        customer = chargify.Customer('customer_attributes')
        customer.first_name = cleaned_data.get('first_name')
        customer.last_name = cleaned_data.get('last_name')
        customer.email = cleaned_data.get('email')

        creditcard = chargify.CreditCard('credit_card_attributes')
        creditcard.full_number = cleaned_data.get('cc_number')
        creditcard.expiration_month = cleaned_data.get('month')
        creditcard.expiration_year = cleaned_data.get('year')
        creditcard.billing_zip = cleaned_data.get('cc_zip')

        subscription = chargify.Subscription()
        subscription.product_handle = settings.DEFAULT_PRODUCT_HANDLE
        subscription.customer = customer
        subscription.credit_card = creditcard

        success, obj = subscription.save()
        if not success:
            raise forms.ValidationError('There was an error processing your card information.')
        self.subscription = obj

    def save(self):
        instance = super(SignupForm, self).save(commit=False)
        instance.subscription_id = self.subscription.id
        instance.customer_id = self.subscription.customer.id
        cleaned_data = self.cleaned_data
        first_name = cleaned_data['first_name']
        last_name = cleaned_data['last_name']
        email = cleaned_data['email']
        password = cleaned_data['password1']
        user = User(
            username=hashlib.md5(email).hexdigest()[:30], 
            first_name=first_name, 
            last_name=last_name,
            email=email
        )
        user.set_password(password)
        user.save()
        instance.user = user
        instance.save()
        site = Site()
        site.subdomain = cleaned_data['subdomain']
        site.account = instance
        site.save()


class DomainForm(forms.ModelForm):
    class Meta:
        model = Site
        fields = ('domain',)
