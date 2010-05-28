import httplib
import urllib2

from django.conf import settings
from django.core import mail
from django.core.urlresolvers import reverse
from django.db.models import get_model
from django.template.loader import render_to_string

from celery.task import Task
from facebook import Facebook, FacebookError

from oauth import oauth

from tiger.accounts.models import Subscriber, FaxList
from tiger.notify.fax import FaxServiceError
from tiger.notify.models import Release
from tiger.notify.utils import CONSUMER_KEY, CONSUMER_SECRET, SERVER, update_status


class DeliverOrderTask(Task):
    def run(self, order_id, status):
        from tiger.core.models import Order
        order = Order.objects.get(id=order_id)
        order.notify_restaurant(status)


class SendFaxTask(Task):
    def run(self, release_id, fax_list_id, **kwargs):
        release = Release.objects.get(id=release_id)
        fax_list = FaxList.objects.get(id=fax_list_id)
        try:
            return release.send_fax(fax_list)
        except FaxServiceError, e:
            self.retry([release_id], kwargs,
                countdown=60 * 1, exc=e)


class SendMailChimpTask(Task):
    def run(self, release_id, **kwargs):
        Release = get_model('notify', 'release')
        release = Release.objects.get(id=release_id)
        release.send_mailchimp()
    

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
        kwds = dict(uid=uid, message=msg)
        if href is not None:
            kwds.update({'action_links': [{'title': 'View on our site', 'href': href}]})
        try:
            fb.stream.publish(**kwds)
        except FacebookError, e:
            self.retry([uid, msg, link_title, href], kwargs,
                countdown=60 * 5, exc=e)


class PublishTask(Task):
    def run(self, release_id, twitter=False, facebook=False, mailchimp=False,
            fax_list=None, **kwargs):
        release = Release.objects.get(id=release_id)
        site = release.site
        social = site.social
        msg = release.title
        if release.coupon:
            short_url = reverse('coupon_short_code', kwargs={'item_id': release.coupon.id})
            link_title = 'Use it now'
        else:
            short_url = reverse('press_short_code', kwargs={'item_id': release.id})
            link_title = 'Read on our site'
        short_url = unicode(site) + short_url
        if site.twitter() and twitter:
            msg = ' '.join([msg, short_url]) 
            TweetNewItemTask.delay(msg, social.twitter_token, social.twitter_secret)
        if site.facebook() and facebook:
            PublishToFacebookTask.delay(social.facebook_id, msg, link_title=link_title, href=short_url)
        if mailchimp:
            SendMailChimpTask.delay(release_id=release.id)
        if fax_list:
            SendFaxTask.delay(release_id=release.id, fax_list_id=fax_list.id)
