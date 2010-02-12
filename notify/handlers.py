from tiger.notify.tasks import TweetNewItemTask

def item_social_handler(sender, instance, created, **kwargs):
    if created:
        social = instance.site.social
        url = unicode(instance.site) + instance.get_absolute_url()
        msg = 'New menu item! %s - %s' % (instance.name, url)
        if social.twitter_token and social.twitter_secret:
            TweetNewItemTask.delay(msg, social.twitter_token, social.twitter_secret)
