from datetime import datetime, timedelta
import hashlib
import os

from django.conf import settings
from django.contrib.localflavor.us.models import USStateField, PhoneNumberField
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.contrib.gis.db import models
from django.db.models.signals import post_save
from django.template.loader import render_to_string
from django.template.defaultfilters import slugify
from django.utils import simplejson as json
from django.utils.safestring import mark_safe

import pytz
from pytz import timezone

from tiger.core.exceptions import NoOnlineOrders, ClosingTimeBufferError, RestaurantNotOpen
from tiger.utils.cache import cachedmethod, KeyChain
from tiger.utils.billing import prorate
from tiger.utils.geocode import geocode, GeocodeError
from tiger.utils import hours
from tiger.sales.models import Account, Invoice
from tiger.sms.models import SmsSettings
from tiger.stork import Stork
from tiger.stork.models import Theme

TIMEZONE_CHOICES = zip(pytz.country_timezones('us'), [tz.split('/', 1)[1].replace('_', ' ') for tz in pytz.country_timezones('us')])


class Site(models.Model):
    """Encapsulates data for the domain and other information relevant to
    displaying a specific site.
    """
    account = models.ForeignKey(Account)
    user = models.ForeignKey('auth.User')
    name = models.CharField(max_length=200)
    subdomain = models.CharField(max_length=200, unique=True)
    domain = models.CharField(max_length=200, null=True, blank=True)
    email = models.EmailField(blank=True, null=True)
    custom_domain = models.BooleanField(default=False)
    walkthrough_complete = models.BooleanField(default=False, editable=False)
    theme = models.ForeignKey(Theme, null=True, on_delete=models.SET_NULL)
    sms = models.ForeignKey(SmsSettings, null=True)
    plan = models.ForeignKey('sales.Plan', null=True)
    signup_date = models.DateField(auto_now_add=True)
    managed = models.BooleanField(default=False)
    reseller_network = models.BooleanField('I have this restaurant\'s written consent to send an invitation to its SMS subscribers', default=False)
    credit_card = models.ForeignKey('sales.CreditCard', null=True)
    google_analytics = models.CharField('Google analytics Web Property ID', max_length=30, null=True)
    webmaster_tools = models.TextField(null=True, max_length=255)
    mobile_on = models.BooleanField(default=False)

    def natural_key(self):
        return (self.subdomain,)

    def __unicode__(self):
        if self.custom_domain:
            return 'http://' + self.domain
        else:
            return self.tiger_domain()

    def save(self, *args, **kwargs):
        super(Site, self).save(*args, **kwargs)
        KeyChain.mobile_enabled.invalidate(self.id)

    def tiger_domain(self, secure=False):
        return 'https://%s.takeouttiger.com' % self.subdomain

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
        if availability != hours.TIME_OPEN:
            if availability == hours.TIME_EOD:
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
        from tiger.stork import Stork
        stork = Stork(self.theme)
        return stork['layout'].as_template()

    def skin_url(self):
        return self.theme.bundled_css.url

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

    def create_invoice(self):
        return Invoice.objects.create(
            account=self.account,
            site=self
        )

    def prorate(self, amt):
        return prorate(self.signup_date + timedelta(days=self.account.trial_period), amt)

    @property
    def is_suspended(self):
        return bool(self.account.invoice_set.filter(status=Invoice.STATUS_FAILED).count())

    def send_confirmation_email(self):
        body = render_to_string('accounts/confirmation.txt', {'site': self})
        send_mail('Takeout Tiger signup confirmation', body, settings.DEFAULT_FROM_EMAIL, [self.user.email])

    def enable_orders(self):
        return any(loc.enable_orders for loc in self.location_set.all())

    def order_options(self):
        options = []
        for loc in self.location_set.all():
            for opt in ('delivery', 'takeout', 'dine_in',):
                if getattr(loc, opt, False):
                    options.append(opt.replace('_', '-'))
        return list(set(options))

    def authorized(self, user):
        if self.account.user == user:
            return True
        if self.user == user:
            return True
        if user.is_superuser:
            return True
        return False

    @cachedmethod(KeyChain.menu_json)
    def menu_json(self):
        data = json.dumps([section.for_json() for section in self.section_set.all()])
        md5 = hashlib.md5(data).hexdigest()
        return {
            'data': data,
            'md5': md5
        }

    @cachedmethod(KeyChain.font_data)
    def font_data(self):
        stork = Stork(self.theme)
        data = dict(
            (font.id, {
                'stack': font.instance.font.stack,
                'font_face': font.get_mobile_css()
            })
            for font in stork.fonts
        )
        return {
            'md5': hashlib.md5(json.dumps(data)).hexdigest(),
            'data': data
        }

    @cachedmethod(KeyChain.mobile_enabled)
    def mobile_enabled(self):
        return self.plan.has_mobile and self.mobile_on


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
    enable_orders = models.BooleanField(default=False)

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

    def order_recipient(self):
        if self.receive_via == Location.RECEIPT_EMAIL:
            return self.order_email
        return self.order_fax


class Schedule(models.Model):
    site = models.ForeignKey(Site)
    display = models.TextField(null=True, default='default schedule')
    master = models.BooleanField(default=False)

    def __unicode__(self):
        return self.display or ''

    def save(self, *args, **kwargs):
        super(Schedule, self).save(*args, **kwargs)
        KeyChain.sidebar_locations.invalidate(self.site.id)
        KeyChain.footer_locations.invalidate(self.site.id)

    @models.permalink
    def get_absolute_url(self):
        return 'edit_schedule', (), {'schedule_id': self.id}

    def is_open(self, location, now=None, buff=0):
        if now is None:
            server_tz = timezone(settings.TIME_ZONE)
            now = server_tz.localize(datetime.now())
        return hours.is_available(
            timeslots=self.timeslot_set.all(), 
            location=location,
            now=now,
            buff=buff
        )

    def mobile_schedule(self):
        return hours.calculate_hour_string(self.timeslot_set.all(), for_mobile=True)


class TimeSlot(models.Model):
    schedule = models.ForeignKey(Schedule)
    section = models.ForeignKey('core.Section', null=True, editable=False)
    dow = models.IntegerField(choices=hours.DOW_CHOICES)
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

    def prep(self, location, day, t):
        return location.get_timezone().localize(datetime.combine(day, t))

    def get_availability(self, location, now, buff=0):
        as_tz = now.astimezone(location.get_timezone())
        date_in_tz = as_tz.date()
        start_dt = self.prep(location, date_in_tz, self.start)
        stop_dt = self.prep(location, date_in_tz, self.stop)
        if self.spans_midnight(): 
            if self.is_tomorrow(now):
                start_dt -= timedelta(days=1)
            else:
                stop_dt += timedelta(days=1)
        if start_dt < now < stop_dt:
            if start_dt < now < stop_dt - timedelta(seconds=buff*60):
                return hours.TIME_OPEN
            return hours.TIME_EOD

    def spans_midnight(self):
        return self.stop < self.start

    def is_tomorrow(self, now):
        return now.weekday() % 7 == (self.dow + 1) % 7


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
        schedule = Schedule.objects.create(site=instance, master=True)
        Location.objects.create(site=instance, schedule=schedule)
        theme = Theme.objects.create(name=instance.name)
        sms = SmsSettings.objects.create(reseller_network=instance.reseller_network)
        instance.sms = sms
        stork = Stork(theme)
        stork.save()
        instance.theme = theme
        instance.save()


def refresh_theme(sender, instance, created, **kwargs):
    if not created:
        try:
            site = Site.objects.get(theme=instance)
        except Site.DoesNotExist:
            return
        KeyChain.template.invalidate(site.id)
        KeyChain.skin.invalidate(site.id)
        KeyChain.font_data.invalidate(site.id)


post_save.connect(new_site_setup, sender=Site)
post_save.connect(refresh_theme, sender=Theme)
