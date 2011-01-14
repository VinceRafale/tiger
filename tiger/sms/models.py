from datetime import datetime

from django.db import models
from django.contrib.localflavor.us.models import *
from django.utils import simplejson as json
from tiger.utils.models import Message

import twilio

# Create your models here.

class SmsSettings(models.Model):
    sms_number = PhoneNumberField(null=True)
    sid = models.CharField(max_length=34, null=True)
    send_intro = models.BooleanField(default=False)
    intro_sms = models.CharField(max_length=160, null=True)

    @property
    def enabled(self):
        return bool(self.sms_number)

    def send(self, body):
        #TODO: provide callback URL
        for subscriber in self.subscriber_set.active():
            subscriber.send_message(body, self.sms_number)


class SmsSubscriberManager(models.Manager):
    use_for_related_fields = True

    def active(self):
        return self.filter(unsubscribed_at__isnull=True)


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
        if not self.id:
            self.signed_up_at = datetime.now()
        super(SmsSubscriber, self).save(*args, **kwargs)

    @property
    def is_active(self):
        return not self.unsubscribed_at

    def send_message(self, body, sms_number=None):
        account = twilio.Account(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_ACCOUNT_TOKEN)
        if sms_number is None:
            sms_number = self.settings.sms_number
        response = account.request('/2010-04-01/Accounts/%s/SMS/Messages.json' % settings.TWILIO_ACCOUNT_SID, 'POST', dict(From=sms_number, To=self.phone_number, Body=body))
        data = json.loads(response)
        #TODO: learn more about failures
        SMS.objects.create(
            settings=self.settings,
            subscriber=self,
            body=body,
            direction=SMS.DIRECTION_OUTBOUND
        )


class SMS(Message):
    DELIVERY_PENDING = 0
    DELIVERY_SUCCESS = 1
    DELIVERY_FAILURE = 2
    settings = models.ForeignKey(SmsSettings)
    subscriber = models.ForeignKey(SmsSubscriber)
    sid = models.CharField(max_length=34)
    body = models.CharField(max_length=160)
    status = models.IntegerField(default=DELIVERY_PENDING)
