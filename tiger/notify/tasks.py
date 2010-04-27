import httplib
import urllib2

from django.conf import settings
from django.core import mail
from django.db.models import get_model

from celery.task import Task
from facebook import Facebook, FacebookError

from oauth import oauth

from tiger.accounts.models import Subscriber
from tiger.notify.fax import FaxMachine, FaxServiceError
from tiger.notify.utils import CONSUMER_KEY, CONSUMER_SECRET, SERVER, update_status


class SendFaxTask(Task):
    def run(self, site, recipients, content, **kwargs):
        fax_machine = FaxMachine(site)
        try:
            return fax_machine.send(recipients, content, **kwargs)
        except FaxServiceError, e:
            self.retry([site, recipients, content], kwargs,
                countdown=60 * 1, exc=e)


class SendEmailTask(Task):
    def run(self, msgs, **kwargs):
        connection = mail.get_connection()
        connection.send_messages(msgs)
    

class TweetNewItemTask(Task):
    def run(self, msg, token, secret, **kwargs):
        CONSUMER = oauth.OAuthConsumer(CONSUMER_KEY, CONSUMER_SECRET)
        CONNECTION = httplib.HTTPSConnection(SERVER)
        access_token = oauth.OAuthToken(token, secret) 
        try:
            return update_status(CONSUMER, CONNECTION, access_token, msg)
        except urllib2.HTTPError, e:
            self.retry([msg, token, secret], kwargs,
                countdown=60 * 5, exc=e)


class PublishToFacebookTask(Task):
    def run(self, uid, msg, link_title=None, href=None, **kwargs):
        fb = Facebook(settings.FB_API_KEY, settings.FB_API_SECRET)
        kwargs = dict(uid=uid, msg=msg)
        if href is not None:
            kwargs.update({'action_links': [{'title': 'View on our site', 'href': href}]})
        try:
            fb.stream.publish(**kwargs)
        except FacebookError, e:
            self.retry([uid, msg, link_title, href], kwargs,
                countdown=60 * 5, exc=e)


class PublishTask(Task):
    def run(self, release_id, **kwargs):
        Release = get_model('notify', 'release')
        release = Release.objects.get(id=release_id)
        site = blast.site
        social = site.social
        #content = open(blast.pdf.path).read()
        #via_fax = blast.subscribers.filter(update_via=Subscriber.VIA_FAX)
        #numbers = [s.fax for s in via_fax]
        #names = [contact.user.get_full_name() for contact in via_fax]
        #SendFaxTask.delay(site=site, recipients=numbers, content=content, names=names, PageOrientation=blast.pdf.get_orientation_display())
        if release.coupon:
            msg = unicode(release.coupon)
            short_url = reverse('coupon_short_code', kwargs={'item_id': release.coupon.id})
            link_title = 'Use it now'
        else:
            msg = release.title
            short_url = reverse('press_short_code', kwargs={'item_id': release.id})
            link_title = 'Read on our site'
        if site.twitter():
            msg = ' '.join([msg, short_url]) 
            TweetNewItemTask.delay(msg, social.twitter_token, social.twitter_secret)
        if site.facebook():
            PublishToFacebookTask.delay(social.facebook_id, msg, link_title=link_title, href=short_url)
        release.send_mailchimp()
