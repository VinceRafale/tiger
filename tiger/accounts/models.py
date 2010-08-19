import os
from datetime import date, datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.localflavor.us.models import *
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.db import models
from django.db.models.signals import post_save
from django.template import Template
from django.template.loader import render_to_string

import pytz

from tiger.look.models import Skin
from tiger.utils.cache import cachedmethod, KeyChain
from tiger.utils.geocode import geocode, GeocodeError
from tiger.utils.hours import *

TIMEZONE_CHOICES = zip(pytz.country_timezones('us'), [tz.split('/', 1)[1].replace('_', ' ') for tz in pytz.country_timezones('us')])


class SalesRep(models.Model):
    user = models.ForeignKey(User)
    code = models.CharField(max_length=8)
    plan = models.CharField(max_length=12, default=settings.DEFAULT_BONUS_PRODUCT_HANDLE)


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

    def natural_key(self):
        return (self.user.username,)

    def __unicode__(self):
        return self.company_name

    def save(self, *args, **kwargs):
        if not self.id:
            self.signup_date = date.today()
        super(Account, self).save(*args, **kwargs)

    def send_confirmation_email(self):
        body = render_to_string('accounts/confirmation.txt', {'account': self})
        send_mail('Takeout Tiger signup confirmation', body, settings.DEFAULT_FROM_EMAIL, [self.user.email])


class Site(models.Model):
    """Encapsulates data for the domain and other information relevant to
    displaying a specific site.
    """
    account = models.ForeignKey(Account)
    name = models.CharField(max_length=200, default='Your Restaurant Name')
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
    email = models.EmailField(blank=True, null=True)
    timezone = models.CharField(choices=TIMEZONE_CHOICES, default='US/Eastern', max_length=100)
    custom_domain = models.BooleanField(default=False)
    enable_orders = models.BooleanField(default=False)
    hours = models.CharField(null=True, max_length=255)
    lon = models.DecimalField(max_digits=12, decimal_places=9, null=True, editable=False)
    lat = models.DecimalField(max_digits=12, decimal_places=9, null=True, editable=False)
    walkthrough_complete = models.BooleanField(default=False, editable=False)

    def natural_key(self):
        return (self.subdomain,)

    def __unicode__(self):
        if self.custom_domain:
            return 'http://' + self.domain
        else:
            return self.tiger_domain()

    def save(self, *args, **kwargs):
        if self.address and not (self.lon and self.lat):
            try:
                self.lon, self.lat = [str(f) for f in geocode(self.address)]
            except GeocodeError:
                pass
        super(Site, self).save(*args, **kwargs)

    def tiger_domain(self, secure=False):
        return 'http%s://%s.takeouttiger.com' % (
            's' if secure else '',
            self.subdomain
        )

    @property
    def custom_media_url(self):
        """Returns a path where site-specific static files can be accessed.
        """
        return os.path.join(settings.CUSTOM_MEDIA_URL, self.tiger_domain().lstrip('http://'))        

    @property
    def address(self):
        address_pieces = [self.street, self.city, self.state, self.zip]
        if all(address_pieces):
            return ' '.join(address_pieces)
        return ''

    def calculate_hour_string(self, commit=True):
        """Returns a nicely formatted string representing availability based on the
        site's associated ``TimeSlot`` objects.
        """
        hours = calculate_hour_string(self.timeslot_set.all())
        if commit:
            self.hours = hours
            self.save()
        return self.hours

    @cachedmethod(KeyChain.twitter)
    def twitter(self):
        social = self.social
        if social.twitter_token and social.twitter_secret:
            return social.twitter_screen_name
        return False

    @cachedmethod(KeyChain.facebook)
    def facebook(self):
        social = self.social
        if social.facebook_id and social.facebook_url:
            return social.facebook_url
        return False

    @cachedmethod(KeyChain.mail)
    def mailchimp(self):
        social = self.social
        if social.mailchimp_api_key and social.mailchimp_allow_signup:
            return True
        return False

    @property
    def is_open(self):
        return is_available(
            timeslots=self.timeslot_set.all(), 
            tz=self.timezone,
            buff=self.ordersettings.eod_buffer
        )

    @cachedmethod(KeyChain.pdf)
    def menu(self):
        try:
            return self.pdfmenu_set.get(featured=True)
        except ObjectDoesNotExist:
            return None

    @cachedmethod(KeyChain.news)
    def has_news(self):
        return self.release_set.count()

    @cachedmethod(KeyChain.template)
    def template(self):
        return self._template(self.skin.pre_base)

    def staged_template(self):
        return self._template(self.skin.staged_pre_base)

    def _template(self, html):
        pre_base_shell = """
            {%% extends 'head.html' %%}
            {%% block main %%}%s{%% endblock %%}""" % html
        return Template(pre_base_shell)

    @cachedmethod(KeyChain.skin)
    def skin_url(self):
        return self.skin.url


#class Location(models.Model):
    #site = models.ForeignKey(Site)
    #name = models.CharField(max_length=255, blank=True)
    #street = models.CharField(max_length=255, default='')
    #city = models.CharField(max_length=255, default='')
    #state = USStateField(max_length=255, default='')
    #zip_code = models.CharField(max_length=10, default='')
    #phone = PhoneNumberField(default='')
    #fax_number = PhoneNumberField(default='', blank=True)
    #email = models.EmailField(blank=True, null=True)
    #timezone = models.CharField(choices=TIMEZONE_CHOICES, default='US/Eastern', max_length=100)
    #schedule = models.ForeignKey('Schedule')
    #lon = models.DecimalField(max_digits=12, decimal_places=9, null=True, editable=False)
    #lat = models.DecimalField(max_digits=12, decimal_places=9, null=True, editable=False)

    #def save(self, *args, **kwargs):
        #if self.address and not (self.lon and self.lat):
            #try:
                #self.lon, self.lat = [str(f) for f in geocode(self.address)]
            #except GeocodeError:
                #pass
        #super(Location, self).save(*args, **kwargs)

    #@property
    #def address(self):
        #address_pieces = [self.street, self.city, self.state, self.zip_code]
        #if all(address_pieces):
            #return ' '.join(address_pieces)
        #return ''


class Schedule(models.Model):
    site = models.ForeignKey(Site)
    display = models.TextField(null=True)
    master = models.BooleanField(default=False)

    def __unicode__(self):
        return self.display or ''

    @models.permalink
    def get_absolute_url(self):
        return 'edit_schedule', (), {'schedule_id': self.id}


class TimeSlot(models.Model):
    schedule = models.ForeignKey(Schedule)
    section = models.ForeignKey('core.Section', null=True, editable=False)
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


class FaxList(models.Model):
    site = models.ForeignKey(Site, editable=False)
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name


class Subscriber(models.Model):
    fax_list = models.ForeignKey(FaxList)
    organization = models.CharField('Name', max_length=255)
    fax = PhoneNumberField()

    def __unicode__(self):
        return self.organization


def new_site_setup(sender, instance, created, **kwargs):
    if created:
        Site = models.get_model('accounts', 'site')
        if isinstance(instance, Site):
            schedule = Schedule.objects.create(site=instance)
            #location = Location.objects.create(site=instance, schedule=schedule)


post_save.connect(new_site_setup)
