import os
from datetime import date, datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.localflavor.us.models import *
from django.core.exceptions import ObjectDoesNotExist
from django.db import models

import pytz
from pytz import timezone

from tiger.look.models import Skin

TIMEZONE_CHOICES = zip(pytz.country_timezones('us'), [tz.split('/', 1)[1].replace('_', ' ') for tz in pytz.country_timezones('us')])


class Account(models.Model):
    """Stores data for customer billing and contact.
    """
    user = models.ForeignKey(User)
    company_name = models.CharField(max_length=200)
    email = models.EmailField('billing e-mail address')
    phone = PhoneNumberField()
    fax = PhoneNumberField()
    street = models.CharField(max_length=255)
    state = USStateField()
    zip = models.CharField(max_length=10)
    # customer's authorize.net information for online orders
    auth_net_api_login = models.CharField(max_length=255, blank=True)
    auth_net_api_key = models.CharField(max_length=255, blank=True)
    signup_date = models.DateField(editable=False, default=datetime.now)

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
    subdomain = models.CharField(max_length=200)
    domain = models.CharField(max_length=200, null=True, blank=True)
    enable_blog = models.BooleanField(default=False)
    blog_address = models.URLField(blank=True)
    street = models.CharField(max_length=255, default='')
    city = models.CharField(max_length=255, default='')
    state = USStateField(max_length=255, default='')
    zip = models.CharField(max_length=10, default='')
    phone = PhoneNumberField(default='')
    fax_number = PhoneNumberField(default='', blank=True)
    timezone = models.CharField(choices=TIMEZONE_CHOICES, default='US/Eastern', max_length=100)
    custom_domain = models.BooleanField(default=False)
    enable_orders = models.BooleanField(default=False)
    skin = models.ForeignKey(Skin, default=1)

    def __unicode__(self):
        if self.custom_domain:
            domain = '.'.join(['www', self.domain, self.tld])
        else:
            return self.tiger_domain()
        return 'http://' + domain

    def tiger_domain(self):
        return 'http://%s.takeouttiger.com' % self.domain

    @property
    def custom_media_url(self):
        """Returns a path where site-specific static files can be accessed.
        """
        return os.path.join(settings.CUSTOM_MEDIA_URL, '.'.join([self.domain, self.tld]))        

    @property
    def address(self):
        return ' '.join([self.street, self.city, self.state, self.zip])

    @property
    def hours(self):
        """Returns a nicely formatted string representing availability based on the
        site's associated ``TimeSlot`` objects.
        """
        # this implementation is a little naive, but let's just assume our customers
        # don't keep ridiculous hours
        timeslots = self.timeslot_set.order_by('dow')
        times = {}
        for timeslot in timeslots:
            time_range = '%s-%s' % (timeslot.pretty_start, timeslot.pretty_stop)
            if times.has_key(time_range):
                times[time_range].append(timeslot.dow)
            else:
                times[time_range] = [timeslot.dow]
        time_dict = dict(TimeSlot.DOW_CHOICES)
        time_strings = []
        abbr_length = 3
        time_list = times.items()
        time_list.sort(key=lambda obj: obj[1][0])
        for k, v in time_list:
            # test if the dow ints are consecutive
            if v == range(v[0], v[-1] + 1) and len(v) > 1:
                s = '%s-%s %s' % (time_dict[v[0]][:abbr_length], time_dict[v[-1]][:abbr_length], k)
            else:
                s = '%s %s' % ('/'.join(time_dict[n][:abbr_length] for n in v), k)
            time_strings.append(s)
        return ', '.join(time_strings)

    def twitter(self):
        social = self.social
        if social.twitter_token and social.twitter_secret:
            return social.twitter_screen_name
        return False

    def facebook(self):
        social = self.social
        if social.facebook_id and social.facebook_url:
            return social.facebook_url
        return False

    @property
    def is_open(self):
        server_tz = timezone(settings.TIME_ZONE)
        site_tz = timezone(self.timezone)
        now = server_tz.localize(datetime.now())
        timeslots = self.timeslot_set.filter(dow=now.weekday())
        if not timeslots.count():
            return False
        for timeslot in timeslots:
            start_dt = site_tz.localize(datetime.combine(datetime.now(), timeslot.start))
            stop_dt = site_tz.localize(datetime.combine(datetime.now(), timeslot.stop))
            if start_dt < now < stop_dt:
                return True
        return False

    @property
    def menu(self):
        try:
            return self.pdfmenu_set.get(featured=True)
        except ObjectDoesNotExist:
            return None


class TimeSlot(models.Model):
    DOW_MONDAY = 0
    DOW_TUESDAY = 1
    DOW_WEDNESDAY = 2
    DOW_THURSDAY = 3
    DOW_FRIDAY = 4
    DOW_SATURDAY = 5
    DOW_SUNDAY = 6
    DOW_CHOICES = (
        (DOW_MONDAY, 'Monday'),
        (DOW_TUESDAY, 'Tuesday'),
        (DOW_WEDNESDAY, 'Wednesday'),
        (DOW_THURSDAY, 'Thursday'),
        (DOW_FRIDAY, 'Friday'),
        (DOW_SATURDAY, 'Saturday'),
        (DOW_SUNDAY, 'Sunday'),
    )
    site = models.ForeignKey(Site)
    dow = models.IntegerField(choices=DOW_CHOICES)
    start = models.TimeField()
    stop = models.TimeField()

    def _pretty_time(self, time_obj):
        hour = '12' if time_obj.hour == 12 else str(time_obj.hour % 12)
        if time_obj.minute:
            return hour + time_obj.strftime(':%M%P')
        else:
            return hour + time_obj.strftime('%P')

    @property
    def pretty_start(self):
        return self._pretty_time(self.start)

    @property
    def pretty_stop(self):
        return self._pretty_time(self.stop)


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


class FaxSubscriberManager(models.Manager):
    def get_query_set(self):
        return super(FaxSubscriberManager, self).get_query_set().filter(
            send_updates=True, update_via=Subscriber.VIA_FAX)
        

class EmailSubscriberManager(models.Manager):
    def get_query_set(self):
        return super(EmailSubscriberManager, self).get_query_set().filter(
            send_updates=True, update_via=Subscriber.VIA_EMAIL)


class Subscriber(models.Model):
    VIA_EMAIL = 1
    VIA_FAX = 2
    VIA_CHOICES = (
        (VIA_EMAIL, 'E-mail'),
        (VIA_FAX, 'Fax'),
    )
    user = models.ForeignKey(User)
    site = models.ForeignKey(Site)
    organization = models.CharField(max_length=255, blank=True)
    send_updates = models.BooleanField(default=True)
    update_via = models.IntegerField(default=VIA_EMAIL, choices=VIA_CHOICES)
    fax = PhoneNumberField(blank=True)
    objects = models.Manager()
    via_fax = FaxSubscriberManager()
    via_email = EmailSubscriberManager()

    def __unicode__(self):
        return self.organization or self.user.get_full_name()
