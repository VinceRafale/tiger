import json
import urllib
import urllib2

from django.db.models import get_model
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.http import int_to_base36

import facebook
from celery.task import Task
import oauth2 as oauth

from tiger.notify.fax import FaxServiceError
from tiger.notify.models import Release


class DeliverOrderTask(Task):
    def run(self, order_id, status):
        from tiger.core.models import Order
        order = Order.objects.get(id=order_id)
        order.notify_restaurant(status)


class SendFaxTask(Task):
    def run(self, release_id, fax_list_id, **kwargs):
        from tiger.accounts.models import FaxList
        release = Release.objects.get(id=release_id)
        fax_list = FaxList.objects.get(id=fax_list_id)
        try:
            return release.dispatch_fax(fax_list)
        except FaxServiceError, e:
            self.retry([release_id], kwargs,
                countdown=60 * 1, exc=e)


class SendMailChimpTask(Task):
    def run(self, release_id, **kwargs):
        Release = get_model('notify', 'release')
        release = Release.objects.get(id=release_id)
        release.dispatch_mailchimp()
    

class TweetNewItemTask(Task):
    def run(self, msg, token, secret, release_id=None, **kwargs):
        access_token = oauth.Token(token, secret) 
        consumer = oauth.Consumer(settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET)
        client = oauth.Client(consumer, access_token)
        try:
            response, content = client.request(
                'http://api.twitter.com/1/statuses/update.json', 
                method='POST',
                body=urllib.urlencode({'status': msg})
            )
            if release_id is not None:
                results = json.loads(content)
                msg_id = results['id']
                release = Release.objects.get(id=release_id)
                Release.objects.filter(id=release_id).update(
                    twitter = 'http://twitter.com/%s/status/%s' % (release.site.social.twitter_screen_name, msg_id)
                )
        except urllib2.HTTPError, e:
            self.retry([msg, token, secret], kwargs,
                countdown=60 * 5, exc=e)


class PublishToFacebookTask(Task):
    def run(self, uid, msg, link=None, name=None, release_id=None, **kwargs):
        graph = facebook.GraphAPI(uid)
        kwds = {'message': msg}
        if link is not None:
            kwds.update({
                'link': link,
                'name': name
            })
        try:
            post = graph.put_object("me", "feed", **kwds)
            if release_id is not None:
                release = Release.objects.get(id=release_id)
                msg_id = post['id'].split('_')[1]
                Release.objects.filter(id=release_id).update(
                    facebook = '%s?story_fbid=%s' % (release.site.social.facebook_url, msg_id)
                )
        except facebook.GraphAPIError, e:
            self.retry([uid, msg, link, name], kwargs,
                countdown=60 * 5, exc=e)


class PublishTask(Task):
    def run(self, release_id, twitter=False, fb=False, mailchimp=False,
            fax_list=None, **kwargs):
        release = Release.objects.get(id=release_id)
        site = release.site
        social = site.social
        msg = release.title
        short_url = reverse('press_short_code', kwargs={'item_id': int_to_base36(release.id)})
        link_title = 'Read on our site'
        short_url = unicode(site) + short_url
        if site.twitter() and twitter:
            if release.visible:
                msg = ' '.join([msg, short_url]) 
            TweetNewItemTask.delay(msg, social.twitter_token, social.twitter_secret, release_id=release_id)
        if site.facebook() and fb:
            kwds = {}
            if release.visible:
                kwds.update(dict(name=link_title, link=short_url)) 
            PublishToFacebookTask.delay(social.facebook_page_token, msg, release_id=release_id, **kwds)
        if mailchimp:
            SendMailChimpTask.delay(release_id=release.id)
        if fax_list:
            SendFaxTask.delay(release_id=release.id, fax_list_id=fax_list.id)
