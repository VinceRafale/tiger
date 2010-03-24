from tiger.notify.tasks import TweetNewItemTask, PublishToFacebookTask

def item_social_handler(sender, instance, created, **kwargs):
    if created:
        social = instance.site.social
        url = unicode(instance.site).replace('www.', '') + instance.get_short_url()
        msg = 'We\'ve got a new menu item - %s! ' % instance.name
        if social.twitter_token and social.twitter_secret:
            msg += url
            TweetNewItemTask.delay(msg, social.twitter_token, social.twitter_secret)
        if social.facebook_id:
            PublishToFacebookTask.delay(
                social.facebook_id, 
                msg, 
                link_title='View on our site', 
                href=url)

