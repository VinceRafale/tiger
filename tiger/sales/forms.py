from datetime import date
from hashlib import sha1

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from tiger.accounts.models import Site
from tiger.sales.exceptions import PaymentGatewayError
from tiger.sales.models import Account, Invoice, Plan
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


class CreateResellerAccountForm(BetterModelForm):
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
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError("The two password fields didn't match.")
        return self.cleaned_data['password2']

    def clean(self):
        if not self._errors:
            try:
                self.customer_prof_id, self.payment_prof_id = self.create_payment_profile()
            except PaymentGatewayError:
                raise forms.ValidationError("Unable to process your credit card.")
        return self.cleaned_data

    def create_payment_profile(self):
        from tiger.sales.authnet import CIM
        data = self.cleaned_data
        cim = CIM()
        account_data = {
            'exp_date': u'%d-%02d' % (data.get('year'), data.get('month')),
            'first_name': data.get('first_name'),
            'last_name': data.get('last_name'),
            'card_number': data.get('cc_number')
        }
        return cim.create_cim_profile(**account_data)

    def save(self, commit=True):
        account = super(CreateResellerAccountForm, self).save(commit=False)
        account.customer_id = self.customer_prof_id
        account.subscription_id = self.payment_prof_id
        account.manager = True
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
        )

    def __init__(self, data=None, account=None, *args, **kwargs):
        super(CreateSiteForm, self).__init__(data, *args, **kwargs)
        self.fields['plan'].queryset = account.plan_set.all()
        self.account = account

    def clean_subdomain(self):
        """Validate that the subdomain is not already in use.
        """
        try:
            Site.objects.get(domain__iexact=self.cleaned_data['subdomain'])
        except Site.DoesNotExist:
            return self.cleaned_data['subdomain']
        raise forms.ValidationError("That subdomain is already in use.")

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
        return site


class CreatePlanForm(BetterModelForm):
    class Meta:
        model = Plan
        exclude = ('account',)
