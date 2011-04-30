from datetime import date, datetime
from decimal import Decimal

from dateutil.relativedelta import *

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.localflavor.us.models import *
from django.core.mail import send_mail
from django.db import models, connection
from django.db.models.signals import post_save
from django.template.loader import render_to_string

from tiger.sales.exceptions import (PaymentGatewayError, 
    SiteManagementError, SoftCapExceeded, HardCapExceeded)
from tiger.sms.models import SmsSettings
from tiger.utils.billing import prorate


class SalesRep(models.Model):
    user = models.ForeignKey(User)
    code = models.CharField(max_length=8)
    plan = models.CharField(max_length=12, default='')

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
    basic_price = models.DecimalField(max_digits=5, decimal_places=2, default='40.00')
    ecomm_price = models.DecimalField(max_digits=5, decimal_places=2, default='67.50')
    multi_price = models.DecimalField(max_digits=5, decimal_places=2, default='85.50')
    sms_line_price = models.DecimalField(max_digits=5, decimal_places=2, default='2.00')
    sms_price = models.DecimalField(max_digits=5, decimal_places=2, default='0.02')
    fax_price = models.DecimalField(max_digits=5, decimal_places=2, default='0.07')
    manager = models.BooleanField(default=False)
    sms = models.ForeignKey('sms.SmsSettings', null=True)

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

    def running_total(self):
        fax_total = self.fax_pages_for_month() * self.fax_price
        sms_total = self.text_messages_for_month() * self.sms_price
        base_plan_total = sum([
            prorate(s.signup_date, s.plan.total)
            for s in self.site_set.all()
        ])
        return base_plan_total + fax_total + sms_total



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

    def _from_account_or_default(self, attr_name, dec):
        account = self.account
        return getattr(account, attr_name, None) or Decimal(dec)

    @property
    def monthly_cost(self):
        account = self.account
        if not self.has_online_ordering:
            return self._from_account_or_default('basic_price', '50.00')
        if not self.multiple_locations:
            return self._from_account_or_default('ecomm_price', '75.00')
        return self._from_account_or_default('multi_price', '95.00')

    @property
    def fax_page_cost(self):
        return self._from_account_or_default('fax_price', '0.10')

    @property
    def sms_number_cost(self):
        return self._from_account_or_default('sms_line_price', '5.00')

    @property
    def sms_cost(self):
        return self._from_account_or_default('sms_price', '0.05')

    @property
    def total(self):
        return self.monthly_cost + self.sms_number_cost

    def _assert_cap_not_exceeded(self, service, num):
        cap = getattr(self, '%s_cap' % service)
        if 0 < cap < num:
            cap_type = getattr(self, '%s_cap_type' % service)
            if cap_type == Plan.CAP_SOFT:
                raise SoftCapExceeded
            elif cap_type == Plan.CAP_HARD:
                raise HardCapExceeded
        return True

    def assert_sms_cap_not_exceeded(self, num):
        return self._assert_cap_not_exceeded('sms', num)
        



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
    date = models.DateField(null=True, default=date.today)

    class Meta:
        ordering = ('-date',)

    def save(self, *args, **kwargs):
        managed_site = self.site and self.site.managed
        new = not self.id
        if managed_site and not self.invoice:
            raise SiteManagementError
        super(Invoice, self).save(*args, **kwargs)
        if self.site and new:
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
        site = self.site
        plan = site.plan
        monthly_cost = plan.monthly_cost
        return site.prorate(monthly_cost)

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
        if self.subinvoice_set.count():
            return sum(self._total(inv) for inv in self.subinvoice_set.all())
        return self._total(self)

    def _total(self, invoice):
        return sum(
            getattr(invoice, attr) 
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

    def send_to_gateway(self):
        from tiger.sales.authnet import Cim
        cim = Cim()
        cim.create_profile_transaction(self.total, self.account.customer_id, self.account.subscription_id, self.id)

    def arrears_date(self):
        return (self.date + relativedelta(months=-1)).replace(day=1)


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
    charge_type = models.IntegerField(choices=CHARGE_CHOICES)
    amount = models.DecimalField(max_digits=7, decimal_places=2)


class Payment(models.Model):
    pass


def set_up_account(sender, instance, created, **kwargs):
    if created:
        sms = SmsSettings.objects.create()
        instance.sms = sms
        instance.save()


post_save.connect(set_up_account, sender=Account)
