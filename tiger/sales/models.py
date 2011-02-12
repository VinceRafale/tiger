import calendar
from datetime import date, datetime
from decimal import Decimal

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.localflavor.us.models import *
from django.core.mail import send_mail
from django.db import models, connection
from django.template.loader import render_to_string

from dateutil.relativedelta import *

from tiger.sales.exceptions import PaymentGatewayError, SiteManagementError


class SalesRep(models.Model):
    user = models.ForeignKey(User)
    code = models.CharField(max_length=8)
    plan = models.CharField(max_length=12, default=settings.DEFAULT_BONUS_PRODUCT_HANDLE)

    class Meta:
        db_table = 'accounts_salesrep'


class Account(models.Model):
    """Stores data for customer billing and contact.
    """
    STATUS_ACTIVE = 1
    STATUS_COMPONENT_SUSPENSION = 2
    STATUS_FULL_SUSPENSION = 3
    STATUS_CHOICES = (
        (STATUS_ACTIVE, 'Active'),
        (STATUS_COMPONENT_SUSPENSION, 'Components suspended'),
        (STATUS_FULL_SUSPENSION, 'All service suspended'),
    )
    user = models.ForeignKey(User)
    company_name = models.CharField(max_length=200)
    email = models.EmailField('billing e-mail address')
    phone = PhoneNumberField(null=True, blank=True)
    fax = PhoneNumberField(null=True, blank=True)
    street = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    state = USStateField(null=True, blank=True)
    zip = models.CharField(max_length=10)
    signup_date = models.DateField(editable=False, default=datetime.now)
    customer_id = models.CharField(max_length=200, default='')
    subscription_id = models.CharField(max_length=200, default='')
    card_number = models.CharField('credit card number', max_length=30, null=True)
    card_type = models.CharField(max_length=50, null=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=STATUS_COMPONENT_SUSPENSION)
    manager = models.BooleanField(default=False)

    class Meta:
        db_table = 'accounts_account'

    def __unicode__(self):
        return self.company_name

    def save(self, *args, **kwargs):
        new = False
        if not self.id:
            self.signup_date = date.today()
            new = True
        super(Account, self).save(*args, **kwargs)
        if new:
            body = render_to_string('sales/reseller_welcome.txt', {'account': self})
            send_mail('Welcome to the Takeout Tiger reseller program', body, settings.DEFAULT_FROM_EMAIL, [self.user.email])

    def send_confirmation_email(self):
        body = render_to_string('accounts/confirmation.txt', {'account': self})
        send_mail('Takeout Tiger signup confirmation', body, settings.DEFAULT_FROM_EMAIL, [self.user.email])

    def set_sms_subscription(self, subscribed):
        raise NotImplementedError

    def create_invoice(self):
        sites = self.site_set.all()
        if sites.filter(managed=True).count():
            invoice = Invoice.objects.create(account=self)
            for site in sites:
                Invoice.objects.create(
                    invoice=invoice,
                    site=site,
                    account=self
                )
            return invoice
        else:
            return sites[0].create_invoice()

    def fax_pages_for_month(self):
        first_of_month = datetime.now().replace(day=1, hour=0, minute=0)
        cursor = connection.cursor()
        cursor.execute("""select sum(f.page_count) from notify_fax f
        join accounts_site s on f.site_id = s.id
        join accounts_account a on a.id = s.account_id
        where a.id = %s and f.timestamp >= %s""", [self.id, first_of_month])
        return cursor.fetchall()[0][0]

    def text_messages_for_month(self):
        first_of_month = datetime.now().replace(day=1, hour=0, minute=0)
        cursor = connection.cursor()
        cursor.execute("""select count(*) from sms_sms sms
        join sms_smssettings settings on sms.settings_id = settings.id
        join accounts_site site on settings.id = site.sms_id
        join accounts_account acct on acct.id = site.account_id
        where acct.id = %s and sms.timestamp >= %s""", [self.id, first_of_month])
        return cursor.fetchall()[0][0]


class Plan(models.Model):
    CAP_SOFT = 1
    CAP_HARD = 2
    CAP_TYPE_CHOICES = (
        (CAP_SOFT, 'Soft cap'),
        (CAP_HARD, 'Hard cap'),
    )
    account = models.ForeignKey(Account, null=True)
    name = models.CharField(max_length=20)
    multiple_locations = models.BooleanField(default=False, blank=True)
    has_online_ordering = models.BooleanField(default=False, blank=True)
    has_sms = models.BooleanField(default=False, blank=True)
    sms_cap = models.IntegerField(default=0)
    sms_cap_type = models.IntegerField(choices=CAP_TYPE_CHOICES, default=0)
    fax_cap = models.IntegerField(default=0)
    fax_cap_type = models.IntegerField(choices=CAP_TYPE_CHOICES, default=0)

    def __unicode__(self):
        return self.name

    @property
    def monthly_cost(self):
        if not self.account:
            if not self.has_online_ordering:
                return Decimal('50.00')
            if not self.multiple_locations:
                return Decimal('75.00')
            return Decimal('95.00')
        if not self.has_online_ordering:
            return Decimal('40.00')
        if not self.multiple_locations:
            return Decimal('67.50')
        return Decimal('85.50')

    @property
    def fax_page_cost(self):
        if not self.account:
            return Decimal('0.10')
        return Decimal('0.07')

    @property
    def sms_number_cost(self):
        if not self.account:
            return Decimal('5.00')
        return Decimal('2.00')

    @property
    def sms_cost(self):
        if not self.account:
            return Decimal('0.05')
        return Decimal('0.02')


class Invoice(models.Model):
    STATUS_UNBILLED = 1
    STATUS_SUCCESS = 2
    STATUS_FAILED = 3
    STATUS_CHOICES = (
        (STATUS_UNBILLED, 'Unbilled',),
        (STATUS_SUCCESS, 'Success',),
        (STATUS_FAILED, 'Failed',),
    )
    account = models.ForeignKey(Account)
    site = models.ForeignKey('accounts.Site', null=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=STATUS_UNBILLED)
    invoice = models.ForeignKey('self', related_name='subinvoice_set', null=True)

    def save(self, *args, **kwargs):
        managed_site = self.site and self.site.managed
        if managed_site and not self.invoice:
            raise SiteManagementError
        super(Invoice, self).save(*args, **kwargs)
        if self.site:
            self.create_charges()

    def create_charges(self):
        Charge.objects.create(
            invoice=self,
            charge_type=Charge.CHARGE_BASE,
            amount=self.main_billing_amount()
        )
        Charge.objects.create(
            invoice=self,
            charge_type=Charge.CHARGE_FAX_USAGE,
            amount=self.get_fax_charge_amount()
        )
        Charge.objects.create(
            invoice=self,
            charge_type=Charge.CHARGE_SMS_NUMBER,
            amount=self.get_sms_number_amount()
        )
        Charge.objects.create(
            invoice=self,
            charge_type=Charge.CHARGE_SMS_USAGE,
            amount=self.get_sms_usage_amount()
        )

    def main_billing_amount(self):
        today = date.today()
        site = self.site
        plan = site.plan
        one_month_ago = today + relativedelta(months=-1)
        monthly_cost = plan.monthly_cost
        if one_month_ago.replace(day=1) > site.signup_date.replace(day=1):
            return monthly_cost
        weekday, days = calendar.monthrange(one_month_ago.year, one_month_ago.month)
        days_in_service = days - site.signup_date.day
        return monthly_cost * (days_in_service / days)

    def get_fax_charge_amount(self):
        unlogged_faxes = self.site.fax_set.filter(logged=False)
        page_count = sum(fax.page_count or 0 for fax in unlogged_faxes)
        unlogged_faxes.update(logged=True)
        return page_count * self.site.plan.fax_page_cost

    def get_sms_number_amount(self):
        return self.site.plan.sms_number_cost

    def get_sms_usage_amount(self):
        unlogged_texts = self.site.sms.sms_set.filter(logged=False)
        sms_count = unlogged_texts.count()
        unlogged_texts.update(logged=True)
        return sms_count * self.site.plan.sms_cost

    @property
    def monthly_fee(self):
        return self._charge_for_type(Charge.CHARGE_BASE)

    @property
    def fax_charges(self):
        return self._charge_for_type(Charge.CHARGE_FAX_USAGE)

    @property
    def sms_number_charges(self):
        if self.site.sms.enabled:
            return self._charge_for_type(Charge.CHARGE_SMS_NUMBER)
        return 0

    @property
    def sms_usage_charges(self):
        return self._charge_for_type(Charge.CHARGE_SMS_USAGE)

    @property
    def total(self):
        return sum(
            getattr(self, attr) 
            for attr in (
                'monthly_fee', 
                'fax_charges', 
                'sms_number_charges', 
                'sms_usage_charges'
            )
        )

    def _charge_for_type(self, charge_type):
        try:
            monthly_charge = self.charge_set.get(charge_type=charge_type)
        except Charge.DoesNotExist:
            return 0
        return monthly_charge.amount

    def charge(self):
        try:
            self.send_to_gateway()
        except PaymentGatewayError:
            self.status = Invoice.STATUS_FAILED
            subject = ''
            body = ''
        else:
            self.status = Invoice.STATUS_SUCCESS
            subject = ''
            body = ''
        self.save()
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [self.account.email])

    def send_to_gateway():
        pass


class Charge(models.Model):
    CHARGE_BASE = 1
    CHARGE_SMS_NUMBER = 2
    CHARGE_SMS_USAGE = 3
    CHARGE_FAX_USAGE = 4
    CHARGE_CHOICES = (
        (CHARGE_BASE, 'Base monthly fee'),
        (CHARGE_SMS_NUMBER, 'Monthly fee for SMS number'),
        (CHARGE_SMS_USAGE, 'SMS usage fees'),
        (CHARGE_FAX_USAGE, 'Fax usage fees'),
    )
    invoice = models.ForeignKey(Invoice)
    charge_type = models.IntegerField()
    amount = models.DecimalField(max_digits=7, decimal_places=2)


class Payment(models.Model):
    pass
