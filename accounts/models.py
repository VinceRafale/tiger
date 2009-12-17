import os
from datetime import date

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.localflavor.us.models import *
from django.db import models


class Site(models.Model):
    domain = models.CharField(max_length=200)
    tld = models.CharField(max_length=4)
    enable_blog = models.BooleanField()
    blog_address = models.URLField()

    @property
    def custom_media_url(self):
        return os.path.join(CUSTOM_MEDIA_ROOT, '.'.join([self.domain, self.tld]))        


class Account(models.Model):
    """Stores data for customer billing and contact.
    """
    user = models.ForeignKey(User)
    site = models.ForeignKey(Site)
    email = models.EmailField()
    phone = PhoneNumberField()
    fax = PhoneNumberField()
    street = models.CharField(max_length=255)
    state = USStateField()
    zip = models.CharField(max_length=10)
    # customer's authorize.net information for online orders
    auth_net_api_login = models.CharField(max_length=255, blank=True)
    auth_net_api_key = models.CharField(max_length=255, blank=True)
    signup_date = models.DateField(editable=False)
    # Takeout Tiger's authorize.net information for this customer in CIM
    customer_profile_id = models.IntegerField()
    payment_profile_id = models.IntegerField()
    cc_last_4 = models.CharField(blank=True, max_length=16)

    def save(self, *args, **kwargs):
        if not self.id:
            self.signup_date = date.today()
        super(Account, self).save(*args, **kwargs)


#TODO: nice clean way to handle enabled services (fax, e-mail, SMS, voice)
# and tracking usage

class Invoice(models.Model):
    account = models.ForeignKey(Account)
    date = models.DateField()


class LineItem(models.Model):
    invoice = models.ForeignKey(Invoice)
    description = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    qty = models.IntegerField()
    total = models.DecimalField(max_digits=9, decimal_places=2)

    def save(self, *args, **kwargs):
        self.total = self.price * self.qty
        super(LineItem, self).save(*args, **kwargs)
