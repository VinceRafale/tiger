from datetime import datetime
import random

from django.contrib.localflavor.us.models import *
from django.db import models, connection
from django.utils import simplejson as json

import twilio

from tiger.utils.fields import PickledObjectField
from tiger.utils.models import Message

# Create your models here.

class SmsSettings(models.Model):
    sms_number = PhoneNumberField(null=True)
    sid = models.CharField(max_length=34, null=True)
    send_intro = models.BooleanField('send an automated introductory SMS when someone first subscribes', default=False, blank=True)
    intro_sms = models.CharField(max_length=160, null=True)

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


class SmsSubscriberManager(models.Manager):
    use_for_related_fields = True

    def active(self):
        return self.filter(unsubscribed_at__isnull=True)

    def inactive(self):
        return self.filter(unsubscribed_at__isnull=False)


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
    objects = SmsSubscriberManager()

    def save(self, *args, **kwargs):
        new = not self.id
        if new:
            self.signed_up_at = datetime.now()
        super(SmsSubscriber, self).save(*args, **kwargs)
        if new and self.settings.send_intro:
            self.send_message(self.settings.intro_sms)

    @property
    def is_active(self):
        return not self.unsubscribed_at

    def send_message(self, body, sms_number=None, campaign=None):
        if sms_number is None:
            sms_number = self.settings.sms_number
        data = self.get_sms_response(body, sms_number)
        #TODO: learn more about failures
        SMS.objects.create(
            settings=self.settings,
            campaign=campaign,
            subscriber=self,
            body=body,
            destination=SMS.DIRECTION_OUTBOUND
        )

    def get_sms_response(self, body, sms_number): 
        account = twilio.Account(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_ACCOUNT_TOKEN)
        response = account.request('/2010-04-01/Accounts/%s/SMS/Messages.json' % settings.TWILIO_ACCOUNT_SID, 'POST', dict(From=sms_number, To=self.phone_number, Body=body))
        return json.loads(response)


class Campaign(models.Model):
    settings = models.ForeignKey(SmsSettings, editable=False)
    title = models.CharField('title (for your reference later)', max_length=255)
    body = models.CharField(max_length=160)
    timestamp = models.DateTimeField(editable=False, auto_now_add=True)
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
        sms_number = self.settings.sms_number
        for subscriber in self.subscribers.all():
            subscriber.send_message(self.body, self.sms_number)
            self.sent_count += 1
            self.save()
        self.completed = True
        self.save()

    def img_url(self):
        urls = {
            None: 'both_stars.png',
            False: 'unstarred.png',
            True: 'Favourite_24x24.png',
        }
        return urls[self.starred]
            


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
    read = models.BooleanField()

    def save(self, *args, **kwargs):
        super(SMS, self).save(*args, **kwargs)
        if self.body.strip().lower() == 'out':
            subscriber = self.subscriber
            subscriber.unsubscribed_at = datetime.now()
            subscriber.save()
