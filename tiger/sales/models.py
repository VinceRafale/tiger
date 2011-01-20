from datetime import date, datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.localflavor.us.models import *
from django.db import models


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
    referrer = models.ForeignKey(SalesRep, null=True, editable=False)
    status = models.IntegerField(choices=STATUS_CHOICES, default=STATUS_COMPONENT_SUSPENSION)

    class Meta:
        db_table = 'accounts_account'

    def __unicode__(self):
        return self.company_name

    def save(self, *args, **kwargs):
        if not self.id:
            self.signup_date = date.today()
        super(Account, self).save(*args, **kwargs)

    def send_confirmation_email(self):
        body = render_to_string('accounts/confirmation.txt', {'account': self})
        send_mail('Takeout Tiger signup confirmation', body, settings.DEFAULT_FROM_EMAIL, [self.user.email])

    def set_sms_subscription(self, subscribed):
        chargify = Chargify(settings.CHARGIFY_API_KEY, settings.CHARGIFY_SUBDOMAIN)
        chargify.subscriptions.components.update(
            subscription_id=self.subscription_id, component_id=2889, 
            data={'component': {'enabled': int(subscribed)}}
        )
