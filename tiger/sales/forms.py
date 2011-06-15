from datetime import date
from decimal import Decimal
from hashlib import sha1

import yaml

from django import forms
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import transaction

from tiger.accounts.models import Site
from tiger.sales.exceptions import PaymentGatewayError
from tiger.sales.models import Account, Invoice, Plan, CreditCard
from tiger.sms.models import SmsSettings
from tiger.utils.forms import BetterModelForm


class AuthenticationForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, data=None, request=None, *args, **kwargs):
        self.request = request
        super(AuthenticationForm, self).__init__(data, *args, **kwargs)

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email and password:
            self.user_cache = authenticate(email=email, password=password)
            if self.user_cache is None:
                raise forms.ValidationError("Please enter a correct username and password. Note that both fields are case-sensitive.")
            elif not self.user_cache.is_active:
                raise forms.ValidationError("This account is inactive.")

        # TODO: determine whether this should move to its own method.
        if self.request:
            if not self.request.session.test_cookie_worked():
                raise forms.ValidationError("Your Web browser doesn't appear to have cookies enabled. Cookies are required for logging in.")

        return self.cleaned_data

    def get_user(self):
        return self.user_cache


class SignupRedirectForm(forms.Form):
    promo_code = forms.CharField(label="Please enter your promo code")

    def clean_promo_code(self):
        promo_code = self.cleaned_data.get('promo_code')
        try:
            plan = Plan.objects.get(promo_code=promo_code)
        except Plan.DoesNotExist:
            raise forms.ValidationError("Sorry, that's not a valid promo code.")
        self.plan = plan
        return promo_code


class CreditCardForm(BetterModelForm):
    cc_number = forms.CharField(label='Card number')
    month = forms.CharField()
    year = forms.CharField()

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
        if not self._errors:
            try:
                self.customer_prof_id, self.payment_prof_id = self.create_payment_profile()
            except PaymentGatewayError:
                raise forms.ValidationError("Unable to process your credit card.")
        return self.cleaned_data

    def create_payment_profile(self):
        from tiger.sales.authnet import Cim
        data = self.cleaned_data
        cim = Cim()
        account_data = {
            'expiration_date': u'%d-%02d' % (data.get('year'), data.get('month')),
            'first_name': data.get('first_name'),
            'last_name': data.get('last_name'),
            'card_number': data.get('cc_number'),
            'email': data.get('email')
        }
        return cim.create_cim_profile(**account_data)

    def save(self, commit=True):
        instance = super(CreditCardForm, self).save(commit=False)
        self.credit_card = CreditCard.objects.create(
            customer_id = self.customer_prof_id,
            subscription_id = self.payment_prof_id,
            card_number = self.cleaned_data.get('cc_number')[-4:]
        )
        return instance


class CreateResellerAccountForm(CreditCardForm):
    first_name = forms.CharField()
    last_name = forms.CharField()
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm password', widget=forms.PasswordInput)

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

    def clean_password2(self):
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError("The two password fields didn't match.")
        return self.cleaned_data['password2']

    def save(self, commit=True):
        account = super(CreateResellerAccountForm, self).save(commit=False)
        account.credit_card = self.credit_card
        account.manager = True
        account.sms = SmsSettings.objects.create()
        email = self.cleaned_data.get('email')
        user = User(
            username=sha1(email).hexdigest()[:30],
            first_name=self.cleaned_data.get('first_name'),
            last_name=self.cleaned_data.get('last_name'),
            email=email
        )
        user.set_password(self.cleaned_data.get('password1'))
        user.save()
        account.user = user
        if commit:
            account.save()
        return account


class SiteSignupForm(CreditCardForm):
    subdomain = forms.CharField()
    first_name = forms.CharField()
    last_name = forms.CharField()
    site_name = forms.CharField(label='Restaurant name')
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm password', widget=forms.PasswordInput)
    email = forms.EmailField()
    zip = forms.CharField()

    class Meta:
        model = Site
        fields = ('subdomain',)

    def __init__(self, data=None, account=None, plan=None, *args, **kwargs):
        self.account = account
        self.plan = plan
        super(SiteSignupForm, self).__init__(data, *args, **kwargs)

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

    def clean_password2(self):
        """Verify that the values entered into the two password fields
        match. Note that an error here will end up in
        ``non_field_errors()`` because it doesn't apply to a single
        field.
        """
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError("The two password fields didn't match.")

    def save(self, commit=True):
        site = super(SiteSignupForm, self).save(commit=False)
        site.credit_card = self.credit_card
        site.managed = True
        site.account = self.account
        site.plan = self.plan
        email = self.cleaned_data.get('email')
        user = User(
            username=sha1(email).hexdigest()[:30],
            first_name=self.cleaned_data.get('first_name'),
            last_name=self.cleaned_data.get('last_name'),
            email=email
        )
        user.set_password(self.cleaned_data.get('password1'))
        user.save()
        site.user = user
        if commit:
            site.save()
            site.send_confirmation_email()
        return site


class EditSiteForm(BetterModelForm):
    class Meta:
        model = Site
        fields = ('plan',)

    def __init__(self, data=None, account=None, *args, **kwargs):
        super(EditSiteForm, self).__init__(data, *args, **kwargs)


class CreateSiteForm(BetterModelForm):
    subdomain = forms.CharField()

    class Meta:
        model = Site
        fields = (
            'name',
            'subdomain',
            'email',
            'plan',
            'reseller_network',
        )

    def __init__(self, data=None, account=None, *args, **kwargs):
        super(CreateSiteForm, self).__init__(data, *args, **kwargs)
        self.fields['plan'].queryset = account.plan_set.all()
        self.account = account

    def clean_subdomain(self):
        """Validate that the subdomain is not already in use.
        """
        try:
            Site.objects.get(subdomain__iexact=self.cleaned_data['subdomain'])
        except Site.DoesNotExist:
            return self.cleaned_data['subdomain']
        raise forms.ValidationError("That subdomain is already in use.")

    def clean_email(self):
        """Validate that the subdomain is not already in use.
        """
        try:
            User.objects.get(email__iexact=self.cleaned_data['email'])
        except User.DoesNotExist:
            return self.cleaned_data['email']
        raise forms.ValidationError("That e-mail address is already in use.")

    def clean(self):
        data = self.cleaned_data
        if self.account.invoice_set.filter(status=Invoice.STATUS_FAILED).count():
            raise forms.ValidationError('Your most recent invoice could not be processed.  Please update your billing information before creating more sites.')
        return data

    def save(self, commit=True):
        site = super(CreateSiteForm, self).save(commit=False)
        site.account = self.account
        email = self.cleaned_data['email']
        username = sha1(email).hexdigest()[:30]
        site.user = User.objects.create_user(username, email, password=username)
        if commit:
            site.save()
            site.send_confirmation_email()
        return site


class CreatePlanForm(BetterModelForm):
    class Meta:
        model = Plan
        exclude = ('account', 'secret',)

    def clean_promo_code(self):
        promo_code = self.cleaned_data.get('promo_code')
        try:
            plan = Plan.objects.get(promo_code=promo_code)
        except Plan.DoesNotExist:
            return promo_code
        raise forms.ValidationError("That promo code is already taken.")


def set_attributes(obj, obj_type, attrs, defaults=None):
    from tiger.core.models import Upgrade, Variant, SideDishGroup, SideDish
    prices = attrs.get('prices')
    if prices:
        if defaults.get('prices'):
            obj.variant_set.all().delete()
        for p in prices:
            v = Variant(description=p['label'], price=Decimal(str(p.get('price') or '0')))
            setattr(v, obj_type, obj)
            v.save()
    extras = attrs.get('extras')
    if extras:
        if defaults.get('extras'):
            obj.upgrade_set.all().delete()
        for x in extras:
            upg = Upgrade(name=p['label'], price=Decimal(str(p.get('price') or '0')))
            setattr(upg, obj_type, obj)
            upg.save()
    choice_sets = attrs.get('choice_sets')
    if choice_sets:
        if defaults.get('choice_sets'):
            obj.sidedishgroup_set.all().delete()
        for cs in choice_sets:
            group = SideDishGroup()
            setattr(group, obj_type, obj)
            group.save()
            for c in cs['choices']:
                SideDish.objects.create(name=c['label'], price=Decimal(str(c.get('price') or '0')), group=group)


def import_menu(site, raw_data):
    from tiger.core.models import Section, Item
    data = yaml.load(raw_data)
    with transaction.commit_on_success():
        for s in data['sections']:
            section = Section.objects.create(site=site, name=s['name'], description=s.get('description') or '')
            defaults = s.get('defaults')
            if defaults:
                set_attributes(section, 'section', defaults)
            for i in s['items']:
                item = Item(name=i['name'], description=i.get('label') or '', section=section, site=site)
                item.vegetarian = i.get('vegetarian', False)
                item.spicy = i.get('spicy', False)
                item.taxable = i.get('taxable', False)
                if i.get('price_override'):
                    item.available_online = False
                    item.text_price = i['price_override']
                item.save()
                set_attributes(item, 'item', i, defaults)
    


class ImportMenuForm(BetterModelForm):
    import_file = forms.FileField()

    class Meta:
        model = Site
        fields = ()

    def clean_import_file(self):
        upload = self.cleaned_data.get('import_file')
        if not upload:
            raise forms.ValidationError("No file provided.")
        import_menu(self.instance, upload.read())
        return upload
