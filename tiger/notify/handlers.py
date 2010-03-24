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

def coupon_social_handler(sender, instance, created, **kwargs):
    if created:
        social = instance.site.social
        msg = 'Get %d% off your online order at %s with coupon code %s!'
        if instance.exp_date or instance.max_clicks:
            msg += ' Valid '
            if instance.max_clicks:
                msg += 'for the first %d customers ' % instance.max_clicks
            if instance.exp_date:
                msg += 'until %s' % instance.exp_date.strftime('%m/%d/%y')
        TweetNewItemTask.delay(msg, social.twitter_token, social.twitter_secret)
        PublishToFacebookTask.delay(social.facebook_id, msg)

