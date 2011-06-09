from tiger.notify.tasks import TweetNewItemTask, PublishToFacebookTask

def item_social_handler(sender, instance, created, **kwargs):
    #TODO: get Item.STAGE_READY in here for clarity
    if instance.posting_stage == 1:
        social = instance.site.social
        try:
            relative = instance.get_short_url()
        except:
            return
        url = unicode(instance.site).replace('www.', '') + relative 
        msg = 'We\'ve got a new menu item - %s! ' % instance.name
        if all([social.twitter_token, social.twitter_secret, social.twitter_auto_items]):
            msg += url
            TweetNewItemTask.delay(msg, social.twitter_token, social.twitter_secret)
        if social.facebook_page_token and social.facebook_auto_items:
            PublishToFacebookTask.delay(
                social.facebook_page_token, 
                msg, 
                name='View on our site', 
                link=url)
