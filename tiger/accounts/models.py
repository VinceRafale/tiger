import os
from datetime import date, datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.localflavor.us.models import *
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.contrib.gis.db import models
from django.db.models.signals import post_save
from django.template import Template
from django.template.loader import render_to_string
from django.template.defaultfilters import slugify
from django.utils.safestring import mark_safe

import pytz
from pytz import timezone

from tiger.core.exceptions import NoOnlineOrders, ClosingTimeBufferError, RestaurantNotOpen
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
    name = models.CharField(max_length=200)
    subdomain = models.CharField(max_length=200, unique=True)
    domain = models.CharField(max_length=200, null=True, blank=True)
    email = models.EmailField(blank=True, null=True)
    custom_domain = models.BooleanField(default=False)
    enable_orders = models.BooleanField(default=False)
    walkthrough_complete = models.BooleanField(default=False, editable=False)

    def natural_key(self):
        return (self.subdomain,)

    def __unicode__(self):
        if self.custom_domain:
            return 'http://' + self.domain
        else:
            return self.tiger_domain()

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

    @cachedmethod(KeyChain.twitter)
    def twitter(self):
        social = self.social
        if social.twitter_token and social.twitter_secret:
            return social.twitter_screen_name
        return False

    @cachedmethod(KeyChain.facebook)
    def facebook(self):
        social = self.social
        if social.facebook_url:
            return social.facebook_url
        return False

    @cachedmethod(KeyChain.mail)
    def mailchimp(self):
        social = self.social
        if social.mailchimp_api_key and social.mailchimp_allow_signup:
            return True
        return False

    def is_open(self, location):
        if not self.enable_orders:
            # if they don't have online ordering, why proclaim it?
            raise NoOnlineOrders("Invalid data.  Please try again.", '/')
        schedule = location.schedule
        eod_buffer = location.eod_buffer
        availability = schedule.is_open(buff=location.eod_buffer, location=location)
        if availability != TIME_OPEN:
            if availability == TIME_EOD:
                raise ClosingTimeBufferError("Sorry!  Orders must be placed within %d minutes of closing." % eod_buffer, '/')
            raise RestaurantNotOpen("""%s is currently closed. Please try ordering during normal
            restaurant hours, %s.""" % (self.name, schedule.display), '/')
        return True

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

    def localize(self, dt, location):
        site_tz = timezone(location.timezone)
        return site_tz.localize(dt)

    @cachedmethod(KeyChain.footer_locations)
    def footer_locations(self):
        html = render_to_string('core/includes/footer_locations.html', {'site': self}) 
        return mark_safe(html)

    @cachedmethod(KeyChain.sidebar_locations)
    def sidebar_locations(self):
        html = render_to_string('core/includes/sidebar_locations.html', {'site': self}) 
        return mark_safe(html)


class Location(models.Model):
    RECEIPT_EMAIL = 1
    RECEIPT_FAX = 2
    RECEIPT_CHOICES = (
        (RECEIPT_EMAIL, 'E-mail'),
        (RECEIPT_FAX, 'Fax'),
    )
    site = models.ForeignKey(Site)
    name = models.CharField(max_length=255, blank=True)#, help_text='If you have multiple locations, this is how this location will be displayed.  It is also how it will appear in your dashboard\'s list of locations.')
    street = models.CharField(max_length=255, default='')
    city = models.CharField(max_length=255, default='')
    state = USStateField(max_length=255, default='')
    zip_code = models.CharField(max_length=10, default='')
    phone = PhoneNumberField(default='')
    fax_number = PhoneNumberField(default='', blank=True)
    email = models.EmailField(blank=True, null=True)
    timezone = models.CharField(choices=TIMEZONE_CHOICES, default='US/Eastern', max_length=100)
    schedule = models.ForeignKey('Schedule', null=True)
    lon = models.DecimalField(max_digits=12, decimal_places=9, null=True, editable=False)
    lat = models.DecimalField(max_digits=12, decimal_places=9, null=True, editable=False)
    # migrated from core.OrderSettings
    receive_via = models.IntegerField(default=1, choices=RECEIPT_CHOICES)
    dine_in = models.BooleanField(default=True) 
    takeout = models.BooleanField(default=True) 
    order_fax = PhoneNumberField(default='', blank=True)
    order_email = models.EmailField(blank=True, null=True)
    delivery = models.BooleanField(default=True) 
    delivery_minimum = models.DecimalField('minimum amount for delivery orders', max_digits=5, decimal_places=2, default='0.00') 
    lead_time = models.PositiveIntegerField('how many minutes before must a pick-up order be placed in advance?', default=0) 
    delivery_lead_time = models.PositiveIntegerField('how many minutes before must a delivery order be placed in advance?', default=0) 
    delivery_area = models.MultiPolygonField(null=True, blank=True) 
    tax_rate = models.DecimalField(decimal_places=3, max_digits=5, null=True)
    eod_buffer = models.PositiveIntegerField(default=30)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        new = not self.id
        if new and self.schedule is None:
            self.schedule = self.site.schedule_set.get(master=True)
        if self.address and not (self.lon and self.lat):
            try:
                self.lon, self.lat = [str(f) for f in geocode(self.address)]
            except GeocodeError:
                pass
        super(Location, self).save(*args, **kwargs)
        if new:
            from tiger.core.models import LocationStockInfo
            for item in self.site.item_set.all():
                LocationStockInfo.objects.create(location=self, item=item)
        KeyChain.footer_locations.invalidate(self.site.id)
        KeyChain.sidebar_locations.invalidate(self.site.id)

    def get_absolute_url(self):
        return '/find-us/#%s' % self.id_attr()

    def id_attr(self):
        return '-'.join([slugify(self.name), str(self.id)])

    @property
    def address(self):
        address_pieces = [self.street, self.city, self.state, self.zip_code]
        if all(address_pieces):
            return ' '.join(address_pieces)
        return ''

    def can_receive_orders(self):
        return (self.receive_via == Location.RECEIPT_EMAIL and self.order_email) \
            or (self.receive_via == Location.RECEIPT_FAX and self.order_fax)

    def get_timezone(self):
        return timezone(self.timezone)

    def email_display(self):
        email = self.email.replace('@', ' <span>@</span> ').replace('.', ' <span>.</span> ')
        escaped = [] 
        for s in email.split():
            if s not in ('<span>@</span>', '<span>.</span>'):
                escaped.append('%s' % ''.join('&#%s;' % ord(c) for c in s))
            else:
                escaped.append(s)
        return mark_safe(''.join(escaped))


class Schedule(models.Model):
    site = models.ForeignKey(Site)
    display = models.TextField(null=True, default='default schedule')
    master = models.BooleanField(default=False)

    def __unicode__(self):
        return self.display or ''

    @models.permalink
    def get_absolute_url(self):
        return 'edit_schedule', (), {'schedule_id': self.id}

    def is_open(self, location, buff=0):
        return is_available(
            timeslots=self.timeslot_set.all(), 
            location=location,
            buff=buff
        )

class TimeSlot(models.Model):
    schedule = models.ForeignKey(Schedule)
    section = models.ForeignKey('core.Section', null=True, editable=False)
    dow = models.IntegerField(choices=DOW_CHOICES)
    start = models.TimeField()
    stop = models.TimeField()

    def _pretty_time(self, time_obj):
        hour = '12' if time_obj.hour in (0, 12) else str(time_obj.hour % 12)
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

    def prepped_start(self, location):
        return self.site.localize(datetime.combine(date.today(), self.start), location)

    def prepped_stop(self, location):
        stop = self.site.localize(datetime.combine(date.today(), self.stop), location)
        if self.stop < self.start:
            stop += timedelta(days=1)
        return stop

    def get_availability(self, location, buff=0):
        now = self.now()
        start_dt = self.prepped_start(location)
        stop_dt = self.prepped_stop(location)
        server_tz = timezone(settings.TIME_ZONE)
        server_now = server_tz.localize(now)
        if start_dt < server_now < stop_dt:
            if start_dt < server_now < stop_dt - timedelta(seconds=buff*60):
                return TIME_OPEN
            return TIME_EOD

    def now(self):
        return datetime.now()

    @property
    def site(self):
        return self.schedule.site


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
            schedule = Schedule.objects.create(site=instance, master=True)
            location = Location.objects.create(site=instance, schedule=schedule)


post_save.connect(new_site_setup)
