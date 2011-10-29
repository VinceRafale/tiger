from datetime import datetime, date
import random

from django.conf import settings
from django.contrib.localflavor.us.models import *
from django.db import models, connection
from django.utils import simplejson as json
from django.utils.dateformat import format

from pytz import timezone
from picklefield.fields import PickledObjectField

import twilio

from tiger.utils.models import Message
from tiger.sms.sender import Sender, BaseSender

# Create your models here.

class SmsSettings(models.Model):
    """Models can generically point to an instance of this model to provide SMS
    functionality.  Both accounts (for resellers) and sites have an SMS module.

    The ``reseller_network`` field value is copied from that of the site at the
    time that the site is created.
    """
    sms_number = PhoneNumberField(null=True)
    sid = models.CharField(max_length=34, null=True)
    send_intro = models.BooleanField('send an automated introductory SMS when someone first subscribes', default=False, blank=True)
    intro_sms = models.CharField(max_length=140, null=True)
    keywords = PickledObjectField(default='')
    reseller_network = models.BooleanField(default=False)
    display = models.BooleanField('display your SMS number on your homepage', default=False, help_text='If you have more than one opt-in keyword, the top on the list will appear along side your SMS number.  You can drag the keywords in the right-hand column to reorder them.')

    def save(self, *args, **kwargs):
        if not self.id:
            self.keywords = ['in']
        super(SmsSettings, self).save(*args, **kwargs)

    @property
    def enabled(self):
        return bool(self.sms_number)

    def get_options_for(self, attr):
        cursor = connection.cursor()
        cursor.execute("""SELECT DISTINCT sub.%s FROM sms_smssubscriber sub
        INNER JOIN sms_smssettings set ON sub.settings_id = set.id
        WHERE set.id = %%s AND sub.unsubscribed_at IS NULL
        """ % attr, [self.id])
        return json.dumps([r[0] for r in cursor.fetchall() if r[0]])

    def add_keywords(self, *args):
        keywords = self.keywords
        keywords.extend(args)
        self.keywords = list(set(keywords))
        self.save()

    def remove_keywords(self, *args):
        keywords = set(self.keywords) - set(args)
        self.keywords = list(keywords)
        self.save()
        for kw in args:
            SmsSubscriber.objects.filter(settings=self, tag=kw).update(deactivated=True)

    def invite(self, reseller, phone_number):
        if self.enabled:
            sender = BaseSender(reseller, self.intro_sms)
            sender.add_recipients(phone_number)
            sender.send_message()

    def number_display(self):
        def phone_number(val):
            digits = ''.join(v for v in val if v.isalnum() and not v.isalpha())
            if not digits:
                return ''
            digits = digits[-10:]
            return '(%s) %s-%s' % (digits[:3], digits[3:6], digits[6:])
        return phone_number(self.sms_number)


class SmsSubscriberManager(models.Manager):
    use_for_related_fields = True

    def active(self):
        return self.filter(unsubscribed_at__isnull=True, deactivated=False)

    def inactive(self):
        return self.filter(unsubscribed_at__isnull=False)

    def counts_per_tag(self, sms_settings):
        cursor = connection.cursor()
        cursor.execute("""SELECT tag, count(*) FROM sms_smssubscriber 
        WHERE settings_id = %s 
        GROUP BY tag 
        ORDER BY tag
        """, [sms_settings.id])
        return cursor.fetchall()



class SmsSubscriber(models.Model):
    settings = models.ForeignKey(SmsSettings)
    phone_number = PhoneNumberField(null=True, blank=True)
    city = models.CharField(max_length=100, null=True)
    state = USStateField(null=True)
    zip_code = models.CharField(max_length=10, null=True)
    menus_first = models.BooleanField(default=False)
    signed_up_at = models.DateTimeField()
    unsubscribed_at = models.DateTimeField(null=True)
    starred = models.BooleanField(default=False)
    tag = models.CharField(max_length=15)
    deactivated = models.BooleanField(default=False)
    objects = SmsSubscriberManager()

    def save(self, *args, **kwargs):
        new = not self.id
        if new:
            self.signed_up_at = datetime.now()
        super(SmsSubscriber, self).save(*args, **kwargs)
        if new and not self.unsubscribed_at:
            if self.settings.send_intro:
                self.send_message(self.settings.intro_sms, intro=True)
            if self.settings.reseller_network:
                self.invite_to_reseller_network(self.phone_number)

    @property
    def is_active(self):
        return not (self.unsubscribed_at or self.deactivated)

    def send_message(self, body, sms_number=None, campaign=None, intro=False):
        s = self._get_site()
        sender = self.sender(s, body)
        sender.add_recipients(self)
        sender.send_message(intro=intro)

    def sender(self, site, body):
        return Sender(site, body)

    def invite_to_reseller_network(self, phone_number):
        s = self._get_site()
        s.account.sms.invite(s.account, self.phone_number)

    def _get_site(self):
        from tiger.accounts.models import Site
        s = Site.objects.get(sms=self.settings)
        return s


class Campaign(models.Model):
    settings = models.ForeignKey(SmsSettings, editable=False)
    title = models.CharField('title (for your reference later)', max_length=255)
    body = models.CharField(max_length=140)
    timestamp = models.DateTimeField(editable=False, auto_now_add=True)
    keyword = models.CharField(max_length=15)
    filter_on = models.CharField(max_length=100, blank=True, choices=[
        ('city', 'city'),
        ('state', 'state'),
        ('zip_code', 'zip code')
    ])
    filter_value = models.CharField(max_length=100, blank=True)
    starred = models.NullBooleanField(default=None)
    count = models.PositiveIntegerField('max. number of SMSes to send')
    sent_count = models.PositiveIntegerField(default=0, editable=False)
    subscribers = models.ManyToManyField(SmsSubscriber, editable=False)
    completed = models.BooleanField(default=False, editable=False)

    def set_subscribers(self):
        subscribers = self.settings.smssubscriber_set.active()
        if self.keyword:
            subscribers = subscribers.filter(tag__iexact=self.keyword)
        if self.filter_on and self.filter_value:
            subscribers = subscribers.filter(**{self.filter_on: self.filter_value})
        if self.starred is not None:
            subscribers = subscribers.filter(starred=self.starred)
        subscribers = list(subscribers)
        self.count = len(subscribers)
        self.save()
        random.shuffle(subscribers)
        self.subscribers.add(*subscribers[:self.count])

    def queue(self):
        #TODO: provide callback URL
        from tiger.sms.tasks import SmsBroadcastTask
        SmsBroadcastTask.delay(self.id)

    def broadcast(self):
        sender = Sender(self.settings.site_set.all()[0], self.body, campaign=self)
        sender.add_recipients(*list(self.subscribers.all()))
        sender.send_message()
        self.completed = True
        self.save()

    def img_url(self):
        urls = {
            None: 'both_stars.png',
            False: 'unstarred.png',
            True: 'Favourite_24x24.png',
        }
        return urls[self.starred]
            

class SmsManager(models.Manager):
    def inbox_for(self, settings):
        return Thread.objects.filter(settings=settings)

    def thread_for(self, settings, phone_number):
        return self.filter(
            settings=settings, 
            phone_number=phone_number, 
            conversation=True
        ).order_by('timestamp')


class SMS(Message):
    DELIVERY_PENDING = 0
    DELIVERY_SUCCESS = 1
    DELIVERY_FAILURE = 2
    settings = models.ForeignKey(SmsSettings)
    campaign = models.ForeignKey(Campaign, null=True)
    subscriber = models.ForeignKey(SmsSubscriber, null=True)
    sid = models.CharField(max_length=34)
    body = models.CharField(max_length=160)
    status = models.IntegerField(default=DELIVERY_PENDING)
    conversation = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=20)
    objects = SmsManager()

    def save(self, *args, **kwargs):
        super(SMS, self).save(*args, **kwargs)
        if self.body.strip().lower() == 'out':
            subscriber = self.subscriber
            if subscriber is None:
                SmsSubscriber.objects.create(
                    settings=self.settings,
                    phone_number=self.phone_number,
                    unsubscribed_at=datetime.now()
                )
            else:
                subscriber.unsubscribed_at = datetime.now()
                subscriber.save()
        if self.conversation:
            try:
                thread = Thread.objects.get(settings=self.settings, phone_number=self.phone_number)
            except Thread.DoesNotExist:
                if self.destination == SMS.DIRECTION_OUTBOUND:
                    return
                thread = Thread.objects.create(
                    settings=self.settings,
                    phone_number=self.phone_number,
                    timestamp=self.timestamp,
                    body=self.body,
                    tag=self.subscriber.tag if self.subscriber else ''
                )
            else:
                to_update = {
                    'body': self.body,
                    'message_count': SMS.objects.thread_for(settings=self.settings, phone_number=self.phone_number).count()
                }
                if self.destination == SMS.DIRECTION_INBOUND:
                    to_update['unread'] = True
                    to_update['timestamp'] = self.timestamp
                Thread.objects.filter(phone_number=self.phone_number).update(**to_update)

    def get_timestamp(self):
        timestamp = self.timestamp
        if timestamp.date() == date.today():
            format_string = 'P'
        elif timestamp.year == date.today().year:
            format_string = 'n/j/y'
        else:
            format_string = 'M j'
        return format(timestamp, format_string)


class Thread(models.Model):
    settings = models.ForeignKey(SmsSettings)
    phone_number = models.CharField(max_length=20)
    body = models.CharField(max_length=160)
    unread = models.BooleanField(default=True)
    timestamp = models.DateTimeField()
    message_count = models.PositiveIntegerField(default=1)
    tag = models.CharField(max_length=15)

    class Meta:
        ordering = ('-timestamp',)

    def get_timestamp(self):
        timestamp = self.timestamp
        if timestamp.date() == date.today():
            format_string = 'P'
        elif timestamp.year == date.today().year:
            format_string = 'n/j/y'
        else:
            format_string = 'M j'
        return format(timestamp, format_string)
