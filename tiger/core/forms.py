from datetime import date
import re
import urllib
import urllib2

from django import forms
from django.contrib.gis.geos import Point, fromstr, GEOSException
from django.contrib.localflavor.us.forms import *
from django.utils import simplejson

from authorize.aim import Api
from olwidget.widgets import EditableMap

from tiger.core.models import *

GEOCODE_URL = 'http://maps.google.com/maps/api/geocode/json'

class GeocodeError(Exception):
    pass

def geocode(address):
    params = {
        'sensor': 'false',
        'address': address
    }
    try:
        response = urllib2.urlopen('%s?%s' % (GEOCODE_URL, urllib.urlencode(params)))
        json = simplejson.loads(response.read())
        location = json['results'][0]['geometry']['location']
    except:
        raise GeocodeError
    lon = location['lng']
    lat = location['lat']
    return lon, lat


class BaseOrderForm(forms.Form):
    def sidedish_fields(self):
        return [
            field for field in self
            if field.name.startswith('side_')
        ]

def get_order_form(instance):
    """For a given ``instance`` of ``core.models.Item``, returns a form 
    appropriate for completing an order, with a quantity field for all forms,
    radio select for variant (if applicable), and checkboxes for substitutions/
    upgrades (if applicable).
    """
    variants = instance.variant_set.all()
    upgrades = instance.upgrade_set.all()
    sidegroups = instance.sidedishgroup_set.all()
    attrs = {
        'quantity': forms.IntegerField(min_value=1, initial=1),
        'notes': forms.CharField(required=False)
    }
    if variants.count() > 1:
        max = variants.order_by('-price')[0].id
        attrs['variant'] = forms.ModelChoiceField(
            queryset=variants, 
            widget=forms.RadioSelect, 
            empty_label=None, 
            initial=max
        )
    if upgrades.count():
        attrs['upgrades'] = forms.ModelMultipleChoiceField(
            queryset=upgrades, 
            widget=forms.CheckboxSelectMultiple, 
            required=False
        ) 
    for sidegroup in sidegroups:
        attrs['side_%d' % sidegroup.id] = forms.ModelChoiceField(
            queryset=sidegroup.sidedish_set.all(), 
            widget=forms.RadioSelect, 
            empty_label=None
        ) 
    return type('OrderForm', (BaseOrderForm,), attrs) 

class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        exclude = ['site']


def get_item_form(site):
    class ItemForm(forms.ModelForm):
        section = forms.ModelChoiceField(queryset=site.section_set.all())
        class Meta:
            model = Item
            exclude = ['site']
    return ItemForm


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        exclude = ('status',)

    def __init__(self, data=None, site=None, *args, **kwargs):
        super(OrderForm, self).__init__(data, *args, **kwargs)
        self.fields['method'] = forms.TypedChoiceField(
            label='This order is for:',
            coerce=int,
            choices=site.ordersettings.choices,
            widget=forms.RadioSelect
        )
        self.delivery_minimum = site.ordersettings.delivery_minimum
        self.site = site

    def clean_method(self):
        method = self.cleaned_data.get('method')
        if self.total < self.delivery_minimum and method == Order.METHOD_DELIVERY:
            msg = 'Delivery orders must be %.2f or more.' % self.delivery_minimum 
            raise forms.ValidationError(msg)
        return method

    def clean(self):
        cleaned_data = super(OrderForm, self).clean()
        method = self.cleaned_data.get('method')
        if method == Order.METHOD_DELIVERY:
            address_fields = ['street', 'city', 'state', 'zip']
            if not all(cleaned_data.get(field) for field in address_fields):
                msg = 'You must enter an address for delivery.'
                raise forms.ValidationError(msg)
            address = ' '.join(cleaned_data.get(field) for field in address_fields)
            msg = """We apologize, but it appears you are outside of our delivery area.
            Please choose one of the other options or call us at %s.""" % self.site.phone
            try:
                lon, lat = geocode(address)
            except:
                raise forms.ValidationError(msg)
            point = Point(lon, lat)
            area = self.site.ordersettings.delivery_area
            if not area.contains(point):
                raise forms.ValidationError(msg)
        return cleaned_data


class CouponForm(forms.Form):
    coupon_code = forms.CharField(required=False)

    def __init__(self, site=None, *args, **kwargs):
        self.site = site
        super(CouponForm, self).__init__(*args, **kwargs)

    def clean_coupon_code(self):
        code = self.cleaned_data.get('coupon_code')
        if not code:
            raise forms.ValidationError('You did not enter a coupon code.')
        try:
            c = Coupon.objects.get(site=self.site, short_code__iexact=code)
        except Coupon.DoesNotExist:
            raise forms.ValidationError('Please enter a valid coupon code.')
        if not c.is_open:
            raise forms.ValidationError('That coupon code is no longer valid.')
        self.coupon = c
        return code


class CouponCreationForm(forms.ModelForm):
    class Meta:
        model = Coupon


class OrderSettingsForm(forms.ModelForm):
    delivery_area = forms.CharField(required=False)

    class Meta:
        model = OrderSettings
        fields = ('dine_in', 'takeout', 'delivery', 'delivery_minimum', 'delivery_area',)

    def __init__(self, data=None, site=None, *args, **kwargs):
        lon, lat = geocode(site.address)
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


class OrderPaymentForm(forms.ModelForm):
    payment_type = forms.TypedChoiceField(
        label='Collect payment via', 
        widget=forms.RadioSelect, 
        coerce=int,
        choices=OrderSettings.PAYMENT_TYPE_CHOICES)

    class Meta:
        model = OrderSettings
        fields = (
            'require_payment',
            'auth_net_api_login',
            'auth_net_api_key',
            'paypal_email',
            'payment_type',
            'takes_amex',
            'takes_discover',
            'takes_mc',
            'takes_visa',
        )

    def clean(self):
        cleaned_data = super(OrderPaymentForm, self).clean()
        if cleaned_data.get('require_payment'):
            payment_type = cleaned_data.get('payment_type')
            if not payment_type:
                raise forms.ValidationError('You must choose a payment type to receive online payments.')
            if payment_type == OrderSettings.PAYMENT_PAYPAL: 
                if not cleaned_data.get('paypal_email'):
                    raise forms.ValidationError('You must enter your PayPal e-mail address to receive payments via PayPal.')
            else:
                auth_login = cleaned_data.get('auth_net_api_login')
                auth_key = cleaned_data.get('auth_net_api_key')
                if not (auth_login and auth_key):
                    raise forms.ValidationError('You must provide your Authorize.net credentials to receive payments via Authorize.net.')
        return cleaned_data


class AuthNetForm(forms.Form):
    first_name = forms.CharField() 
    last_name = forms.CharField() 
    address = forms.CharField() 
    city = forms.CharField() 
    state = forms.CharField(widget=USStateSelect)
    zip = USZipCodeField()
    card_num = forms.RegexField(
        label='Credit card number',
        regex=r'[\d -]+', 
        error_messages={'invalid': 'Please enter a valid credit card number.'}
    )
    month = forms.CharField()
    year = forms.CharField()
    card_code = forms.IntegerField(label='CCV')

    def __init__(self, data=None, order=None, *args, **kwargs):
        self.order = order
        order_settings = self.order.site.ordersettings
        self.login = order_settings.auth_net_api_login
        self.key = order_settings.auth_net_api_key
        initial = {
            'month': 'MM',
            'year': 'YYYY',
        }
        try:
            initial['first_name'], initial['last_name'] = self.order.name.split(' ')
        except ValueError:
            pass
        initial['address'] = self.order.street
        for attr in ('city', 'state', 'zip'):
            initial[attr] = getattr(self.order, attr, '')
        super(AuthNetForm, self).__init__(data, initial=initial, *args, **kwargs)

    def clean_card_num(self):
        card_num = self.cleaned_data['card_num']
        card_num = re.sub(r' |-', '', card_num)
        return card_num

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
        cleaned_data = self.cleaned_data
        if self._errors:
            return cleaned_data
        data = cleaned_data.copy()
        api = Api(self.login, self.key, delimiter=u'|')
        exp_date = '-'.join([data.pop('month'), data.pop('year')])
        transaction = api.transaction(
            type=u'AUTH_CAPTURE', 
            amount=self.order.total, 
            invoice_num=unicode(self.order.id),
            description=u'Order for %s' % self.order.name,
            exp_date=exp_date,
            **data
        )
        if transaction['reason_code'] != u'1':
            msg = 'We were unable to process your transaction. Please verify that your payment information is correct.' 
            raise forms.ValidationError(msg)
        return cleaned_data


class VariantForm(forms.ModelForm):
    class Meta:
        model = Variant
        exclude = ('section', 'item',)


class UpgradeForm(forms.ModelForm):
    class Meta:
        model = Upgrade
        exclude = ('section', 'item',)


class SideDishForm(forms.ModelForm):
    class Meta:
        model = SideDish
        exclude = ('group',)
