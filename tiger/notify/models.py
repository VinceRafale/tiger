from datetime import datetime

from django.core.cache import cache
from django.db import models
from django.db.models.signals import post_save

from greatape import MailChimp

from tiger.content.models import PdfMenu


class Fax(models.Model):
    DIRECTION_INBOUND = 1
    DIRECTION_OUTBOUND = 2
    DIRECTION_CHOICES = (
        (DIRECTION_INBOUND, 'Inbound'),
        (DIRECTION_OUTBOUND, 'Outbound'),
    )
    site = models.ForeignKey('accounts.Site')
    timestamp = models.DateTimeField(null=True, blank=True)
    page_count = models.IntegerField(null=True, blank=True)
    parent_transaction = models.CharField(max_length=100, null=True)
    transaction = models.CharField(max_length=100)
    completion_time = models.DateTimeField(null=True, blank=True)
    destination = models.CharField(max_length=20, null=True, blank=True)


class Social(models.Model):
    CAMPAIGN_NO_CREATE = 0
    CAMPAIGN_CREATE = 1
    CAMPAIGN_SEND = 2
    CAMPAIGN_CHOICES = (
        (CAMPAIGN_NO_CREATE, 'Do not create campaigns for blasts'),
        (CAMPAIGN_CREATE, 'Create campaigns for blasts that can be sent from MailChimp'),
        (CAMPAIGN_SEND, 'Create and automatically send campaigns for blasts'),
    )
    site = models.OneToOneField('accounts.Site')
    twitter_screen_name = models.CharField(max_length=20, blank=True)
    twitter_token = models.CharField(max_length=255, blank=True)
    twitter_secret = models.CharField(max_length=255, blank=True)
    facebook_id = models.CharField(max_length=20, blank=True, null=True)
    facebook_url = models.TextField(blank=True, null=True)
    mailchimp_api_key = models.CharField(max_length=100, null=True, blank=True)
    mailchimp_list_id = models.CharField(max_length=50, null=True, blank=True)
    mailchimp_list_name = models.CharField(max_length=100, null=True, blank=True)
    mailchimp_allow_signup = models.BooleanField('Provide a signup box on your web site', default=False)
    mailchimp_send_blast = models.IntegerField(
        default=CAMPAIGN_NO_CREATE, choices=CAMPAIGN_CHOICES)

    @property
    def mailchimp_lists(self):
        CACHE_KEY = 'mailchimp_choices-%d' % self.id
        mailchimp_choices = cache.get(CACHE_KEY)
        if mailchimp_choices is None:
            mailchimp = MailChimp(self.mailchimp_api_key)
            mailchimp_choices = [
                (lst['id'], lst['name'])
                for lst in mailchimp.lists()
            ]
            cache.set(CACHE_KEY, mailchimp_choices, 3600)
        return mailchimp_choices


class Blast(models.Model):
    site = models.ForeignKey('accounts.Site')
    name = models.CharField(max_length=50)
    pdf = models.ForeignKey(PdfMenu)
    subscribers = models.ManyToManyField('accounts.Subscriber')
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


def new_site_setup(sender, instance, created, **kwargs):
    if instance.__class__.__name__ == 'Site' and created:
        Social.objects.create(site=instance)


post_save.connect(new_site_setup)
