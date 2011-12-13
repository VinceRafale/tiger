import urllib
from datetime import datetime

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.core.cache import cache
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save
from django.template.defaultfilters import slugify
from django.template.loader import render_to_string
from django.utils import simplejson as json

import facebook
from greatape import MailChimp
from markdown import markdown
import oauth2 as oauth

from tiger.content.models import PdfMenu
from tiger.notify.fax import FaxMachine
from tiger.utils.cache import KeyChain
from tiger.utils.models import Message
from tiger.utils.pdf import render_to_pdf


class Fax(Message):
    site = models.ForeignKey('accounts.Site')
    page_count = models.IntegerField(null=True, blank=True)
    parent_transaction = models.CharField(max_length=100, null=True)
    transaction = models.CharField(max_length=100)
    completion_time = models.DateTimeField(null=True, blank=True)


class SMS(Message):
    pass


class Social(models.Model):
    CAMPAIGN_NO_CREATE = 0
    CAMPAIGN_CREATE = 1
    CAMPAIGN_SEND = 2
    CAMPAIGN_CHOICES = (
        (CAMPAIGN_NO_CREATE, 'Do not create campaigns for blasts'),
        (CAMPAIGN_CREATE, 'Create campaigns for blasts that can be sent from MailChimp'),
        (CAMPAIGN_SEND, 'Create and automatically send campaigns for blasts'),
    )
    MAILCHIMP_CACHE_KEY = 'mailchimp_choices-%d' 
    FACEBOOK_CACHE_KEY = 'facebook_pages-%d' 
    site = models.OneToOneField('accounts.Site')
    twitter_screen_name = models.CharField(max_length=20, blank=True)
    twitter_token = models.CharField(max_length=255, blank=True)
    twitter_secret = models.CharField(max_length=255, blank=True)
    twitter_auto_items = models.BooleanField(default=True)
    facebook_token = models.CharField(max_length=255, blank=True, null=True)
    facebook_page_token = models.CharField(max_length=255, blank=True, null=True)
    facebook_page_name = models.CharField(max_length=255, blank=True, null=True)
    facebook_id = models.CharField(max_length=255, blank=True, null=True)
    facebook_url = models.TextField(blank=True, null=True)
    facebook_auto_items = models.BooleanField(default=True)
    mailchimp_api_key = models.CharField(max_length=100, null=True, blank=True)
    mailchimp_list_id = models.CharField(max_length=50, null=True, blank=True)
    mailchimp_list_name = models.CharField(max_length=100, null=True, blank=True)
    mailchimp_allow_signup = models.BooleanField('Provide a signup box on your web site', default=False)
    mailchimp_send_blast = models.IntegerField(
        default=CAMPAIGN_NO_CREATE, choices=CAMPAIGN_CHOICES)
    mailchimp_from_email = models.EmailField(null=True, blank=True)

    def save(self, *args, **kwargs):
        super(Social, self).save(*args, **kwargs)
        KeyChain.twitter.invalidate(self.site.id)
        KeyChain.facebook.invalidate(self.site.id)
        KeyChain.mail.invalidate(self.site.id)

    @property
    def mailchimp_lists(self):
        CACHE_KEY = Social.MAILCHIMP_CACHE_KEY % self.id
        mailchimp_choices = cache.get(CACHE_KEY)
        if mailchimp_choices is None:
            mailchimp = MailChimp(self.mailchimp_api_key)
            mailchimp_choices = [
                (lst['id'], lst['name'])
                for lst in mailchimp.lists()
            ]
            cache.set(CACHE_KEY, mailchimp_choices, 3600)
        return mailchimp_choices

    @property
    def facebook_pages(self):
        CACHE_KEY = Social.FACEBOOK_CACHE_KEY  % self.id
        pages = cache.get(CACHE_KEY)
        if pages is None:
            graph = facebook.GraphAPI(self.facebook_token)
            accounts = graph.get_connections('me', 'accounts')['data']
            if len(accounts) == 0:
                pages = None
            elif len(accounts) == 1:
                pages = [graph.get_object(accounts[0]['id'])]
                page = pages[0] 
                self.facebook_url = page['link']
                self.facebook_page_token = accounts[0]['access_token']
                self.facebook_page_name = page['name']
                self.save()
            else:
                pages = [
                    dict(access_token=account['access_token'], **graph.get_object(account['id']))
                    for account in accounts
                ]
            cache.set(CACHE_KEY, pages, 3600)
        return pages

    @property
    def facebook_fragment(self):
        pages = self.facebook_pages
        if pages is None:
            return 'dashboard/marketing/includes/no_pages.html'
        if len(pages) == 1 or (self.facebook_page_token and self.facebook_page_name):
            return 'dashboard/marketing/includes/one_page.html'
        return 'dashboard/marketing/includes/select_page.html'


class ReleaseManager(models.Manager):
    use_for_related_fields = True

    def visible(self):
        return self.filter(Q(visible=True) & (Q(publish_time__isnull=True) | Q(publish_time__lte=datetime.now())))


class Release(models.Model):
    site = models.ForeignKey('accounts.Site')
    title = models.CharField(max_length=140)
    slug = models.SlugField(editable=False)
    body = models.TextField(blank=True)
    body_html = models.TextField(blank=True, editable=False)
    pdf = models.ForeignKey(PdfMenu, verbose_name='Select one of your PDF menus', null=True, blank=True)
    time_sent = models.DateTimeField(editable=False)
    publish_time = models.DateTimeField(null=True)
    fax_transaction = models.CharField(null=True, blank=True, max_length=100, editable=False)
    twitter = models.CharField(max_length=200, null=True, editable=False)
    facebook = models.CharField(max_length=200, null=True, editable=False)
    mailchimp = models.CharField(max_length=200, null=True, editable=False)
    visible = models.BooleanField('Under "News" on your site', default=False)
    objects = ReleaseManager()

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.body_html = markdown(self.body)
        if not self.id:
            self.slug = slugify(self.title)[:50]
            self.time_sent = datetime.now()
        super(Release, self).save(*args, **kwargs)

    @models.permalink
    def get_absolute_url(self):
        return 'press_detail', (), {'object_id': self.id, 'slug': self.slug}

    def get_body_html(self):
        return render_to_string('notify/release_mail.html', {'release': self})

    def get_body_text(self):
        return render_to_string('notify/release_mail.txt', {'release': self})
                
    def send_fax(self, fax_list):
        site = self.site
        social = site.social
        fax_machine = FaxMachine(site)
        cover_page = None
        attachment = None
        if self.body:
            cover_page = render_to_pdf('notify/cover_page.html', {'release': self})
            content = cover_page
        if self.pdf:
            attachment = open(self.pdf.path).read()
            content = attachment
        kwargs ={}
        if cover_page and attachment:
            kwargs['FileSizes'] = '%d;%d' % (len(cover_page), len(attachment))
            kwargs['FileTypes'] = 'PDF;PDF'
            content = cover_page + attachment
        fax_numbers = [s.fax for s in fax_list.subscriber_set.all()]
        transaction = fax_machine.send(fax_numbers, content, **kwargs)
        Release.objects.filter(id=self.id).update(
            fax_transaction = transaction
        )
        Fax.objects.create(parent_transaction=transaction, 
            transaction=transaction, site=site)

    def fax_count(self):
        return Fax.objects.filter(parent_transaction=self.fax_transaction).count()


def new_site_setup(sender, instance, created, **kwargs):
    if created:
        Site = models.get_model('accounts', 'site')
        if isinstance(instance, Site):
            Social.objects.create(site=instance)


class ApiCall(models.Model):
    SERVICE_FACEBOOK = 'facebook'
    SERVICE_MAILCHIMP = 'mailchimp'
    SERVICE_TWITTER = 'twitter'
    SERVICE_CHOICES = (
        (SERVICE_FACEBOOK, 'Facebook'),
        (SERVICE_MAILCHIMP, 'MailChimp'),
        (SERVICE_TWITTER, 'Twitter'),
    )
    STATUS_PENDING = 1
    STATUS_SUCCESS = 2
    STATUS_ERROR = 3
    STATUS_CHOICES = (
        (STATUS_PENDING, 'Pending'),
        (STATUS_SUCCESS, 'Success'),
        (STATUS_ERROR, 'Error'),
    )
    release = models.ForeignKey(Release, null=True)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    social = models.ForeignKey(Social)
    service = models.CharField(choices=SERVICE_CHOICES, max_length=20)
    queued_at = models.DateTimeField(editable=False, default=datetime.now)
    finished_at = models.DateTimeField(null=True)
    url = models.URLField(max_length=255, null=True)
    msg = models.CharField(max_length=255, null=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=STATUS_PENDING)
    content = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        new = False
        if not self.id:
            new = True
        super(ApiCall, self).save(*args, **kwargs)
        if new:
            from tiger.notify.tasks import ApiCallTask
            ApiCallTask.delay(self.id)

    def set_status(self, status):
        self.status = status
        if status != ApiCall.STATUS_PENDING:
            self.finished_at = datetime.now()

    def push_to_service(self):
        getattr(self, 'push_to_%s' % self.service)()

    def get_client(self):
        return getattr(self, 'get_%s_client' % self.service)()

    def get_twitter_client(self):
        access_token = oauth.Token(self.social.twitter_token, self.social.twitter_secret) 
        consumer = oauth.Consumer(settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET)
        return oauth.Client(consumer, access_token)

    def get_facebook_client(self):
        return facebook.GraphAPI(self.social.facebook_page_token)

    def get_mailchimp_client(self):
        return MailChimp(self.social.mailchimp_api_key)

    def push_to_twitter(self):
        client = self.get_client()
        response, content = client.request(
            'http://api.twitter.com/1/statuses/update.json', 
            method='POST',
            body=urllib.urlencode({'status': self.content})
        )
        results = json.loads(content)
        if 'error' in results:
            self.msg = results['error']
            self.set_status(ApiCall.STATUS_ERROR)
        else:
            msg_id = results['id']
            self.url = 'http://twitter.com/%s/status/%s' % (self.social.twitter_screen_name, msg_id)
            self.set_status(ApiCall.STATUS_SUCCESS)
        self.save()

    def push_to_facebook(self):
        data = self.content_object.get_api_data()
        graph = self.get_client()
        # The following should all be pushed into a get_api_data method for various things...
        """
        kwds = {'message': data['title']}
        if site.facebook() and fb:
            kwds = {}
            if release.visible:
                kwds.update(dict(name=link_title, link=short_url)) 
        if link is not None:
            kwds.update({
                'link': content.short_url(),
                'name': content.link_title()
            })
        """
        try:
            post = graph.put_object("me", "feed", **data)
        except facebook.GraphAPIError, e:
            self.set_status(ApiCall.STATUS_ERROR)
            self.msg = e.messages
        else:
            msg_id = post['id'].split('_')[1]
            self.url = '%s?story_fbid=%s' % (social.facebook_url, msg_id)
            self.set_status(ApiCall.STATUS_SUCCESS)
        self.save()

    def push_to_mailchimp(self):
        release = self.release
        site = release.site
        social = site.social
        if social.mailchimp_send_blast != Social.CAMPAIGN_NO_CREATE:
            mailchimp = MailChimp(social.mailchimp_api_key)
            try:
                campaign_id = mailchimp.campaignCreate(
                    type='regular',
                    options={
                        'list_id': social.mailchimp_list_id,
                        'subject': release.title,
                        'from_email': social.mailchimp_from_email,
                        'from_name': site.name,
                        'to_name': '%s subscribers' % site.name,
                    },
                    content={
                        'html': release.get_body_html(),
                        'text': release.get_body_text()
                })
            except Exception, e:
                self.set_status(ApiCall.STATUS_ERROR)
                self.msg = 'Campaign could not be created.'
                self.save()
                raise
            data_center = social.mailchimp_api_key.split('-')[1]
            self.url = 'http://%s.admin.mailchimp.com/campaigns/show?id=%s' % (data_center, campaign_id)
            if social.mailchimp_send_blast == Social.CAMPAIGN_SEND:
                try:
                    mailchimp.campaignSendNow(cid=campaign_id)
                except Exception, e:
                    self.set_status(ApiCall.STATUS_ERROR)
                    self.msg = 'Campaign created but failed to send.'
                    self.save()
                    raise
                self.set_status(ApiCall.STATUS_SUCCESS)
            self.save()


post_save.connect(new_site_setup)
