from datetime import date
import re
import urllib
import urllib2

from django import forms
from django.contrib.gis.geos import Point
from django.contrib.localflavor.us.forms import *
from django.forms.extras.widgets import SelectDateWidget

from authorize.aim import Api
from pytz import timezone

from tiger.core.exceptions import PricePointNotAvailable
from tiger.core.fields import SelectableTimeField
from tiger.core.models import *
from tiger.dashboard.widgets import ImageChooserWidget
from tiger.utils.forms import BetterModelForm
from tiger.utils.geocode import geocode, GeocodeError



class BaseOrderForm(forms.Form):
    label = forms.CharField(required=False, label='Enter a name here and we\'ll label this item for that person.')

    def __init__(self, data=None, location=None, *args, **kwargs):
        super(BaseOrderForm, self).__init__(data, *args, **kwargs)
        self.location = location

    def clean_variant(self):
        variant = self.cleaned_data.get('variant')
        if variant is not None:
            try:
                variant.is_available(self.location)
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
        'notes': forms.CharField(required=False, label='Special instructions ("No MSG", "Extra lettuce")')
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
    ready_by = SelectableTimeField(required=True)
    day = forms.DateField(required=False, widget=SelectDateWidget())

    class Meta:
        model = Order
        exclude = ('status', 'unread', 'ready_by', 'session_key',)

    def __init__(self, data=None, request=None, *args, **kwargs):
        super(OrderForm, self).__init__(data, *args, **kwargs)
        self.request = request
        site = self.site = request.site
        location = self.location = request.location
        self.fields['method'] = forms.TypedChoiceField(
            label='This order is for:',
            coerce=int,
            choices=site.ordersettings.choices,
            widget=forms.RadioSelect
        )
        self.delivery_minimum = location.delivery_minimum

    def clean_method(self):
        method = self.cleaned_data.get('method')
        if self.total < self.delivery_minimum and method == Order.METHOD_DELIVERY:
            msg = 'Delivery orders must be %.2f or more.' % self.delivery_minimum 
            raise forms.ValidationError(msg)
        return method

    def clean_day(self):
        day = self.cleaned_data.get('day')
        if not day:
            return day
        if day <= date.today():
            raise forms.ValidationError("Order-ahead date must be in the future.")
        return day

    def clean(self):
        cleaned_data = super(OrderForm, self).clean()
        method = self.cleaned_data.get('method')
        location = self.site.location_set.all()[0]
        if method == Order.METHOD_DELIVERY:
            address_fields = ['street', 'city', 'state', 'zip']
            if not all(cleaned_data.get(field) for field in address_fields):
                msg = 'You must enter an address for delivery.'
                raise forms.ValidationError(msg)
            address = ' '.join(cleaned_data.get(field) for field in address_fields)
            msg = """We apologize, but it appears you are outside of our delivery area.
            Please choose one of the other options or call us at %s.""" % location.phone
            try:
                lon, lat = geocode(address)
            except:
                raise forms.ValidationError(msg)
            point = Point(lon, lat)
            area = location.delivery_area
            if not area.contains(point):
                raise forms.ValidationError(msg)
            lead_time = location.delivery_lead_time
        else:
            lead_time = location.lead_time
        ready_by = self.cleaned_data.get('ready_by')
        method_display = dict(Order.METHOD_CHOICES).get(method)
        if ready_by and method_display:
            # check that there is not a date discrepancy across time zones
            loc_zone = self.location.get_timezone()
            day = self.cleaned_data.get('day')
            if day is None:
                day = timezone(settings.TIME_ZONE).localize(datetime.now()).astimezone(loc_zone).date()
            ready_by = loc_zone.localize(datetime.combine(day, ready_by))
            server_tz = timezone(settings.TIME_ZONE)
            if ready_by < server_tz.localize(datetime.now() + timedelta(minutes=lead_time)):
                raise forms.ValidationError('%s orders must be placed %d minutes in advance.' % (method_display, lead_time))
        return cleaned_data

    def save(self, commit=True):
        instance = super(OrderForm, self).save(commit=False)
        request = self.request
        instance.total = request.cart.total()
        instance.tax = request.cart.taxes()
        cart = request.cart.session.get_decoded()
        instance.cart = cart
        instance.session_key = request.cart.session.session_key
        instance.site = self.site
        instance.location = self.location
        if commit:
            instance.save()
        return instance


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
