import hashlib
from datetime import time, date

from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.gis.geos import Point, fromstr, GEOSException
from django.contrib.localflavor.us.us_states import STATE_CHOICES
from django.contrib.localflavor.us.forms import *

from olwidget.widgets import EditableMap

from tiger.accounts.models import (Account, Subscriber, Site, TimeSlot, 
    SalesRep, FaxList, Schedule, Location)
from tiger.utils.chargify import Chargify, ChargifyError
from tiger.utils.forms import BetterModelForm
from tiger.utils.geocode import geocode, GeocodeError


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
        if all(isinstance(v, time) for v in cleaned_data.values()):
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
        self.fields['schedule'].queryset = site.schedule_set.all()


class LocationForm(BetterModelForm):
    class Meta:
        model = Location
        fields = (
            'name',
            'street',
            'city',
            'state',
            'zip_code',
            'phone',
            'fax_number',
            'email',
            'timezone',
            'schedule',
            'tax_rate',
        )

    def address_fields(self):
        return [
            field for field in self
            if field.name in ('city', 'state', 'zip_code')
        ]
    
    def non_address_fields(self):
        return [
            field for field in self
            if field.name not in ('name', 'street', 'city', 'state', 'zip_code', 'tax_rate')
        ]


class OrderSettingsForm(BetterModelForm):
    receive_via = forms.TypedChoiceField(
        widget=forms.RadioSelect, choices=Location.RECEIPT_CHOICES, coerce=int)
    order_email = forms.EmailField(label='E-mail address for receiving orders', required=False)
    order_fax = USPhoneNumberField(label='Fax number for receiving orders', required=False)

    class Meta:
        model = Location
        fields = (
            'dine_in', 
            'eod_buffer',
            'takeout', 
            'delivery', 
            'delivery_area',
            'delivery_minimum', 
            'lead_time',
            'delivery_lead_time',
            'receive_via',
            'order_email',
            'order_fax',
        )

    def __init__(self, data=None, site=None, *args, **kwargs):
        location = kwargs['instance']
        try:
            lon, lat = float(location.lon), float(location.lat)
        except TypeError:
            raise GeocodeError
        super(OrderSettingsForm, self).__init__(data, *args, **kwargs)
        self.fields['delivery_area'].widget = EditableMap(options={
            'geometry': 'polygon',
            'isCollection': True,
            'layers': ['google.streets'],
            'default_lat': lat,
            'default_lon': lon,
            'defaultZoom': 13,
            'map_options': {
                'controls': ['Navigation', 'PanZoom']
            }
        })
        self.fields['order_email'].initial = location.email
        self.fields['order_fax'].initial = location.fax_number
        self.site = site

    def clean(self):
        cleaned_data = super(OrderSettingsForm, self).clean()
        if cleaned_data.get('delivery') and not cleaned_data.get('delivery_area'):
            raise forms.ValidationError('You must map out your delivery area to offer delivery orders.')
        return cleaned_data

    def _post_clean(self):
        delivery_area = self.cleaned_data.get('delivery_area')
        if delivery_area is not None:
            try:
                fromstr(delivery_area)
            except GEOSException:
                self._update_errors({'delivery_area': 'FAIL'})
                return
        super(OrderSettingsForm, self)._post_clean()

    def clean_delivery_area(self):
        area = self.cleaned_data.get('delivery_area')
        if area == '':
            return None
        return area

    def clean_email(self):
        email = self.cleaned_data.get('email')
        via_email = self.cleaned_data['receive_via'] == Location.RECEIPT_EMAIL
        if via_email and not email:
            raise forms.ValidationError('You must specify an e-mail address to receive orders via e-mail.')
        return email

    def clean_fax(self):
        fax = self.cleaned_data.get('fax')
        via_fax = self.cleaned_data['receive_via'] == Location.RECEIPT_FAX
        if via_fax and not fax:
            raise forms.ValidationError('You must specify a fax number to receive orders via fax.')
        return fax


class BasicInfoForm(BetterModelForm):
    class Meta:
        model = Site
        fields = ('name',)
