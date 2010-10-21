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

from tiger.core.exceptions import PricePointNotAvailable
from tiger.accounts.forms import AmPmTimeField
from tiger.core.models import *
from tiger.dashboard.widgets import ImageChooserWidget
from tiger.utils.forms import BetterModelForm
from tiger.utils.geocode import geocode, GeocodeError



class BaseOrderForm(forms.Form):
    def clean_variant(self):
        variant = self.cleaned_data.get('variant')
        if variant is not None:
            try:
                variant.is_available
            except PricePointNotAvailable, e:
                raise forms.ValidationError(e.msg)
        return variant

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
        if sidegroup.sidedish_set.count() > 1:
            attrs['side_%d' % sidegroup.id] = forms.ModelChoiceField(
                queryset=sidegroup.sidedish_set.all(), 
                widget=forms.RadioSelect, 
                empty_label=None
            ) 
    return type('OrderForm', (BaseOrderForm,), attrs) 

class SectionForm(BetterModelForm):
    class Meta:
        model = Section
        exclude = ['site', 'hours']

    def __init__(self, data=None, site=None, *args, **kwargs):
        super(SectionForm, self).__init__(data=data, *args, **kwargs)


def get_item_form(site):
    class ItemForm(BetterModelForm):
        taxable = forms.BooleanField(label='Is this item taxable?', required=False)
        section = forms.ModelChoiceField(queryset=site.section_set.all())
        class Meta:
            model = Item
            exclude = ['site']
        def __init__(self, data=None, *args, **kwargs):
            super(ItemForm, self).__init__(data=data, *args, **kwargs)
            self.fields['image'].widget = ImageChooserWidget(site=site)
    return ItemForm


class OrderForm(forms.ModelForm):
    ready_by = AmPmTimeField(required=True)

    class Meta:
        model = Order
        exclude = ('status', 'unread', 'pickup', 'session_key',)

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

    def clean_ready_by(self):
        ready_by = self.cleaned_data.get('ready_by')
        if not ready_by:
            raise forms.ValidationError('This field is required.')
        today = date.today()
        return self.site.localize(datetime.combine(today, ready_by))

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
            lead_time = self.site.ordersettings.delivery_lead_time
        else:
            lead_time = self.site.ordersettings.lead_time
        ready_by = self.cleaned_data.get('ready_by')
        method_display = dict(Order.METHOD_CHOICES).get(method)
        if ready_by and method_display:
            server_tz = timezone(settings.TIME_ZONE)
            if ready_by < server_tz.localize(datetime.now() + timedelta(minutes=lead_time)):
                raise forms.ValidationError('%s orders must be placed %d minutes in advance.' % (method_display, lead_time))
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


class CouponCreationForm(BetterModelForm):
    discount_type = forms.TypedChoiceField(coerce=int, choices=Coupon.DISCOUNT_CHOICES, widget=forms.RadioSelect, initial=1)

    class Meta:
        model = Coupon
    
    def clean_dollars_off(self):
        discount_type = self.cleaned_data.get('discount_type')
        dollars_off = self.cleaned_data.get('dollars_off')
        if discount_type == Coupon.DISCOUNT_DOLLARS and dollars_off is None:
            raise forms.ValidationError('You must enter dollar amount if you choose a dollar-based discount.') 
        return dollars_off

    def clean_percent_off(self):
        discount_type = self.cleaned_data.get('discount_type')
        percent_off = self.cleaned_data.get('percent_off')
        if discount_type == Coupon.DISCOUNT_PERCENT:
            if percent_off is None:
                raise forms.ValidationError('You must enter a percentage if you choose a percentage-based discount.')
            elif type(percent_off) == int and not 0 < percent_off <= 100:
                raise forms.ValidationError('Please enter a percentage between 1% and 100%.')
        return percent_off

    def clean_exp_date(self):
        exp_date = self.cleaned_data.get('exp_date')
        if exp_date and exp_date <= date.today():
            raise forms.ValidationError('Please enter an expiration date in the future.')
        return exp_date


class OrderSettingsForm(BetterModelForm):
    receive_via = forms.TypedChoiceField(
        widget=forms.RadioSelect, choices=OrderSettings.RECEIPT_CHOICES, coerce=int)
    email = forms.EmailField(label='E-mail address for receiving orders', required=False)
    fax = USPhoneNumberField(label='Fax number for receiving orders', required=False)

    class Meta:
        model = OrderSettings
        fields = (
            'dine_in', 
            'eod_buffer',
            'takeout', 
            'delivery', 
            'delivery_minimum', 
            'lead_time',
            'delivery_lead_time',
            'receive_via',
        )

    def __init__(self, data=None, site=None, *args, **kwargs):
        try:
            lon, lat = float(site.lon), float(site.lat)
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
        self.fields['email'].initial = site.email
        self.fields['fax'].initial = site.fax_number
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
        via_email = self.cleaned_data['receive_via'] == OrderSettings.RECEIPT_EMAIL
        if via_email and not email:
            raise forms.ValidationError('You must specify an e-mail address to receive orders via e-mail.')
        return email

    def clean_fax(self):
        fax = self.cleaned_data.get('fax')
        via_fax = self.cleaned_data['receive_via'] == OrderSettings.RECEIPT_FAX
        if via_fax and not fax:
            raise forms.ValidationError('You must specify a fax number to receive orders via fax.')
        return fax


class OrderMessageForm(forms.ModelForm):
    class Meta:
        model = OrderSettings
        fields = (
            'review_page_text', 
            'send_page_text',
        )


class OrderPaymentForm(BetterModelForm):
    payment_type = forms.TypedChoiceField(
        label='Collect payment via', 
        widget=forms.RadioSelect, 
        coerce=int,
        choices=OrderSettings.PAYMENT_TYPE_CHOICES)

    class Meta:
        model = OrderSettings
        fields = (
            'tax_rate',
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
        payment_type = cleaned_data.get('payment_type')
        if cleaned_data.get('require_payment'):
            if not payment_type:
                raise forms.ValidationError('You must choose a payment type to receive online payments.')
        if payment_type == OrderSettings.PAYMENT_PAYPAL: 
            if not cleaned_data.get('paypal_email'):
                raise forms.ValidationError('You must enter your PayPal e-mail address to receive payments via PayPal.')
        elif payment_type == OrderSettings.PAYMENT_AUTHNET:
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
        exp_date = '-'.join([str(data.pop('month')), str(data.pop('year'))])
        transaction = api.transaction(
            type=u'AUTH_CAPTURE', 
            amount=self.order.total_plus_tax(), 
            invoice_num=unicode(self.order.id),
            description=u'Order for %s' % self.order.name,
            exp_date=unicode(exp_date),
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

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if not price:
            return '0.00'
        return price
