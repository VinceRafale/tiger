from datetime import date
import urllib
import urllib2

from django import forms
from django.contrib.gis.geos import Point, fromstr, GEOSException
from django.contrib.localflavor.us.forms import USPhoneNumberField
from django.utils import simplejson

from olwidget.widgets import EditableMap

from tiger.accounts.forms import AmPmTimeField
from tiger.core.models import *

GEOCODE_URL = 'http://maps.google.com/maps/api/geocode/json'

def geocode(address):
    params = {
        'sensor': 'false',
        'address': address
    }
    response = urllib2.urlopen('%s?%s' % (GEOCODE_URL, urllib.urlencode(params)))
    json = simplejson.loads(response.read())
    location = json['results'][0]['geometry']['location']
    lon = location['lng']
    lat = location['lat']
    return lon, lat

def get_order_form(instance):
    """For a given ``instance`` of ``core.models.Item``, returns a form 
    appropriate for completing an order, with a quantity field for all forms,
    radio select for variant (if applicable), and checkboxes for substitutions/
    upgrades (if applicable).
    """
    variants = instance.variant_set.all()
    upgrades = instance.upgrade_set.all()
    attrs = {
        'quantity': forms.IntegerField(min_value=1, initial=1),
        'notes': forms.CharField(required=False)
    }
    if variants.count() > 1:
        max = variants.order_by('-price')[0].id
        attrs['variant'] = forms.ModelChoiceField(queryset=variants, widget=forms.RadioSelect, empty_label=None, initial=max)
    if upgrades.count():
        attrs['upgrades'] = forms.ModelMultipleChoiceField(queryset=upgrades, widget=forms.CheckboxSelectMultiple, required=False) 
    return type('OrderForm', (forms.Form,), attrs) 

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
        exclude = ('site',)

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
