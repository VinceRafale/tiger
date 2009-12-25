import os
from datetime import date

from crontab import CronTab

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.localflavor.us.models import *
from django.db import models


class Account(models.Model):
    """Stores data for customer billing and contact.
    """
    user = models.ForeignKey(User)
    company_name = models.CharField(max_length=200)
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
    customer_profile_id = models.IntegerField(null=True, blank=True)
    payment_profile_id = models.IntegerField(null=True, blank=True)
    cc_last_4 = models.CharField(blank=True, max_length=16)

    def __unicode__(self):
        return self.company_name

    def save(self, *args, **kwargs):
        if not self.id:
            self.signup_date = date.today()
        super(Account, self).save(*args, **kwargs)


class Site(models.Model):
    """Encapsulates data for the domain and other information relevant to
    displaying a specific site.
    """
    account = models.ForeignKey(Account)
    name = models.CharField(max_length=200)
    domain = models.CharField(max_length=200)
    tld = models.CharField(max_length=4)
    enable_blog = models.BooleanField()
    blog_address = models.URLField(blank=True)

    def __unicode__(self):
        return '.'.join(['www', self.domain, self.tld])

    @property
    def custom_media_url(self):
        """Returns a path where site-specific static files can be accessed.
        """
        return os.path.join(settings.CUSTOM_MEDIA_URL, '.'.join([self.domain, self.tld]))        


class NotificationSettings(models.Model):
    DOW_SUNDAY = 0
    DOW_MONDAY = 1
    DOW_TUESDAY = 2
    DOW_WEDNESDAY = 3
    DOW_THURSDAY = 4
    DOW_FRIDAY = 5
    DOW_SATURDAY = 6
    DOW_CHOICES = (
        (DOW_SUNDAY, 'Sunday'),
        (DOW_MONDAY, 'Monday'),
        (DOW_TUESDAY, 'Tuesday'),
        (DOW_WEDNESDAY, 'Wednesday'),
        (DOW_THURSDAY, 'Thursday'),
        (DOW_FRIDAY, 'Friday'),
        (DOW_SATURDAY, 'Saturday'),
    )
    site = models.OneToOneField(Site)
    notification_time = models.TimeField(null=True, blank=True)
    notification_weekday = models.IntegerField(null=True, blank=True, choices=DOW_CHOICES)

    def save(self, *args, **kwargs):
        cron_command = self._get_cron_command()
        crontab = CronTab()
        try:
            cron = crontab.find_command(cron_command)[0]
        except IndexError:
            cron = None
        if self.notification_time is None and cron is not None:
            crontab.remove(cron)
        else:
            if cron is None:
                cron = crontab.new(cron_command)
            cron.dow.on(self.notification_weekday)
            cron.hour.on(self.notification_time.hour)
            cron.minute.on(self.notification_time.minute)
        crontab.write()
        super(NotificationSettings, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        cron_command = self._get_cron_command()
        crontab = CronTab()
        try:
            cron = crontab.find_command(cron_command)[0]
        except IndexError:
            pass
        else:
            crontab.remove(cron)
            crontab.write()
        super(NotificationSettings, self).delete(*args, **kwargs)

    def _get_cron_command(self):
        site_id = self.site_id
        env_python = os.path.join(settings.PROJECT_ROOT, '../bin/python ')
        cmd = os.path.join(settings.PROJECT_ROOT, 'notification.py')
        return ' '.join([env_python, cmd, str(site_id)])


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
