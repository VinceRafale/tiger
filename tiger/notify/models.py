from datetime import datetime

from django.db import models

from tiger.accounts.models import Site, Subscriber
from tiger.content.models import PdfMenu


class Fax(models.Model):
    DIRECTION_INBOUND = 1
    DIRECTION_OUTBOUND = 2
    DIRECTION_CHOICES = (
        (DIRECTION_INBOUND, 'Inbound'),
        (DIRECTION_OUTBOUND, 'Outbound'),
    )
    site = models.ForeignKey(Site)
    timestamp = models.DateTimeField(null=True, blank=True)
    page_count = models.IntegerField(null=True, blank=True)
    parent_transaction = models.CharField(max_length=100, null=True)
    transaction = models.CharField(max_length=100)
    completion_time = models.DateTimeField(null=True, blank=True)
    destination = models.CharField(max_length=20, null=True, blank=True)


class Social(models.Model):
    site = models.OneToOneField(Site)
    twitter_screen_name = models.CharField(max_length=20, blank=True)
    twitter_token = models.CharField(max_length=255, blank=True)
    twitter_secret = models.CharField(max_length=255, blank=True)
    facebook_id = models.CharField(max_length=20, blank=True, null=True)
    facebook_url = models.TextField(blank=True, null=True)


class Blast(models.Model):
    site = models.ForeignKey(Site)
    name = models.CharField(max_length=50)
    pdf = models.ForeignKey(PdfMenu)
    subscribers = models.ManyToManyField(Subscriber)
    last_sent = models.DateTimeField(editable=False, null=True)
    send_count = models.PositiveIntegerField(default=0)

    def __unicode__(self):
        return self.name

    def send(self):
        from tiger.notify.tasks import RunBlastTask
        self.last_sent = datetime.now()
        self.send_count += 1
        self.save()
        RunBlastTask.delay(self.id)

