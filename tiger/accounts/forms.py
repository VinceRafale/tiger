import hashlib
from datetime import time, date

from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.localflavor.us.us_states import STATE_CHOICES

from tiger.accounts.models import Account, Subscriber, Site, TimeSlot, SalesRep, FaxList, Schedule
from tiger.utils.chargify import Chargify, ChargifyError
from tiger.utils.forms import BetterModelForm


class SubscriberForm(BetterModelForm):
    fax_list = forms.ModelChoiceField(queryset=FaxList.objects.all(), empty_label=None)

    class Meta:
        model = Subscriber

    def __init__(self, data=None, instance=None, site=None, *args, **kwargs):
        super(SubscriberForm, self).__init__(data=data, instance=instance, *args, **kwargs)
        if instance is None:
            del self.fields['fax_list']
        else:
            self.fields['fax_list'].queryset = site.faxlist_set.all()


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
            try:
                t, meridian = value.split()
                h, m = [int(v) for v in t.split(':')]
            except ValueError:
                raise forms.ValidationError('Please entire a clock time, like "12:30 PM".')
            if meridian == 'PM' and h != 12:
                h += 12
            elif meridian == 'AM' and h == 12:
                h = 0
            return time(h, m)
        return None


class LocationForm(BetterModelForm):
    state = forms.ChoiceField(choices=[(abbr, abbr) for abbr, full in STATE_CHOICES])

    class Meta:
        model = Site
        fields = ['name', 'street', 'city', 'state', 'zip', 'phone', 'timezone']


class TimeSlotForm(BetterModelForm):
    start = AmPmTimeField(label='Open', required=False)
    stop = AmPmTimeField(label='Close', required=False)

    class Meta:
        model = TimeSlot
        fields = ['start', 'stop']

    def clean(self):
        super(TimeSlotForm, self).clean()
        cleaned_data = self.cleaned_data
        self.delete = False
        if all(cleaned_data.values()):
            self.noop = False
            return cleaned_data
        if not any(cleaned_data.values()):
            self.noop = True
            if self.instance.id:
                self.delete = True
            return cleaned_data
        raise forms.ValidationError('You must specify an opening and closing time.')

    def save(self, commit=False):
        if self.noop:
            if self.delete:
                self.instance.delete()
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
    promo = forms.CharField(required=False)

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

    def clean_promo(self):
        promo = self.cleaned_data.get('promo', '')
        if promo:
            try:
                rep = SalesRep.objects.get(code=promo)
            except SalesRep.DoesNotExist:
                raise forms.ValidationError('Invalid promo code.')
        return promo

    def clean(self):
        if not self._errors:
            self.process_cc()
        return self.cleaned_data

    def process_cc(self):
        cleaned_data = self.cleaned_data
        if cleaned_data.get('promo'):
            referrer = SalesRep.objects.get(code=cleaned_data['promo'])
            product_handle = referrer.plan
        else:
            product_handle = settings.DEFAULT_PRODUCT_HANDLE
        chargify = Chargify(settings.CHARGIFY_API_KEY, settings.CHARGIFY_SUBDOMAIN)
        try:
            result = chargify.subscriptions.create(data={
                'subscription':{
                    'product_handle': product_handle,
                    'customer_attributes':{
                        'first_name': cleaned_data.get('first_name'),
                        'last_name': cleaned_data.get('last_name'),
                        'email': cleaned_data.get('email')
                    },
                    'credit_card_attributes':{
                        'full_number': cleaned_data.get('cc_number'),
                        'expiration_month': cleaned_data.get('month'),
                        'expiration_year': cleaned_data.get('year'),
                        'billing_zip': cleaned_data.get('cc_zip')
                    }
                }
            })
        except ChargifyError:
            raise forms.ValidationError('There was an error processing your card information.')
        self.subscription = result['subscription']

    def save(self):
        instance = super(SignupForm, self).save(commit=False)
        cleaned_data = self.cleaned_data
        if cleaned_data.get('promo'):
            referrer = SalesRep.objects.get(code=cleaned_data['promo'])
        else:
            referrer = None
        instance.subscription_id = self.subscription['id']
        instance.customer_id = self.subscription['customer']['id']
        instance.card_type = self.subscription['credit_card']['card_type']
        instance.card_number = self.subscription['credit_card']['masked_card_number']
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
        instance.referrer = referrer
        instance.save()
        site = Site()
        site.subdomain = cleaned_data['subdomain']
        site.account = instance
        site.save()
        self.site = site
        return instance


class DomainForm(BetterModelForm):
    domain = forms.URLField(required=True)

    class Meta:
        model = Site
        fields = ('domain',)


class CreditCardForm(BetterModelForm):
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()
    month = forms.CharField()
    year = forms.CharField()

    class Meta:
        model = Account
        fields = (
            'first_name',
            'last_name',
            'card_number',
            'month',
            'year',
            'company_name',
            'phone',
            'fax',
            'street',
            'city',
            'state',
            'zip',
        )

    def __init__(self, *args, **kwargs):
        instance = kwargs['instance']
        user = instance.user
        initial = {
            'first_name': instance.user.first_name,
            'last_name': instance.user.last_name,
            'email': instance.user.email
        }
        super(CreditCardForm, self).__init__(initial=initial,  *args, **kwargs)

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

    def clean(self):
        cleaned_data = super(CreditCardForm, self).clean()
        chargify = Chargify(settings.CHARGIFY_API_KEY, settings.CHARGIFY_SUBDOMAIN)
        subscription_id = self.instance.subscription_id
        try:
            if subscription_id:
                result = chargify.subscriptions.update(subscription_id=subscription_id, data={
                    'subscription': {
                        'customer_attributes':{
                            'first_name': cleaned_data.get('first_name'),
                            'last_name': cleaned_data.get('last_name'),
                            'email': cleaned_data.get('email'),
                            'organization': cleaned_data.get('company_name')
                        },
                        'credit_card_attributes':{
                            'full_number': cleaned_data.get('card_number'),
                            'expiration_month': cleaned_data.get('month'),
                            'expiration_year': cleaned_data.get('year'),
                            'billing_address': cleaned_data.get('street'),
                            'billing_city': cleaned_data.get('city'),
                            'billing_state': cleaned_data.get('state'),
                            'billing_zip': cleaned_data.get('cc_zip')
                        }
                    }
                })
            else:
                result = chargify.subscriptions.create(data={
                    'subscription':{
                        'product_handle': 'chomp',
                        'customer_attributes':{
                            'first_name': cleaned_data.get('first_name'),
                            'last_name': cleaned_data.get('last_name'),
                            'email': cleaned_data.get('email')
                        },
                        'credit_card_attributes':{
                            'full_number': cleaned_data.get('cc_number'),
                            'expiration_month': cleaned_data.get('month'),
                            'expiration_year': cleaned_data.get('year'),
                            'billing_zip': cleaned_data.get('cc_zip')
                        }
                    }
                })
        except ChargifyError, e:
            raise forms.ValidationError('Unable to update your information with our payment processor.')
        self.subscription = result['subscription']
        return cleaned_data


class FaxListForm(forms.ModelForm):
    class Meta:
        model = FaxList
        exclude = ('site',)


class ScheduleSelectForm(forms.Form):
    schedule = forms.ModelChoiceField(queryset=Schedule.objects.all(), empty_label='Available during all business hours')

    def __init__(self, data=None, site=None, *args, **kwargs):
        super(ScheduleSelectForm, self).__init__(data=data, *args, **kwargs)
        self.fields['schedule'].queryset = site.schedule_set.filter(master=False)
