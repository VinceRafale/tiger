from django.db import models

from tiger.accounts.models import Site


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
