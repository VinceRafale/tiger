from tiger.utils.test import TestCase
from django.test.client import Client

from nose.tools import *

from tiger.accounts.models import Site
from tiger.core.models import Coupon


class CouponFeaturesTestCase(TestCase):
    poseur_fixtures = 'tiger.fixtures'
    urls = 'tiger.tiger_urls'
    patch_settings = {
        'tiger.tiger_settings': (
            'MIDDLEWARE_CLASSES',
            'INSTALLED_APPS',
            'TEMPLATE_CONTEXT_PROCESSORS',
        )
    }

    def setUp(self):
        self.site = Site.objects.all()[0]
        self.coupon = Coupon.objects.create(
            site=self.site,
            discount_type=Coupon.DISCOUNT_DOLLARS,
            dollars_off='1.00',
        )
        self.client = Client(HTTP_HOST='www.takeouttiger.com')

    def test_absolute_url_conditions(self):
        coupon = self.coupon
        self.assertEquals(coupon.add_coupon_url(), coupon.get_absolute_url())
        coupon.require_sharing = True
        self.assertEquals(coupon.tiger_url(), coupon.get_absolute_url())

    def test_view_count(self):
        coupon = self.coupon
        coupon.require_sharing = True
        self.client.get(coupon.get_absolute_url())
        self.assertEquals(1, Coupon.objects.get(id=coupon.id).view_count)

    def test_reveal_code_twitter(self):
        coupon = self.coupon
        coupon.require_sharing = True
        response = self.client.post(coupon.get_absolute_url(), {'via': 'twitter'})
        self.assertEquals(1, Coupon.objects.get(id=coupon.id).twitter_share_count)
        self.assertEquals('<a href="%s%s">Redeem now!</a>' % (coupon.site.__unicode__(), coupon.add_coupon_url()), response.content)

    def test_reveal_code_facebook(self):
        coupon = self.coupon
        coupon.require_sharing = True
        response = self.client.post(coupon.get_absolute_url(), {'via': 'facebook'})
        self.assertEquals('<a href="%s%s">Redeem now!</a>' % (coupon.site.__unicode__(), coupon.add_coupon_url()), response.content)
        self.assertEquals(1, Coupon.objects.get(id=coupon.id).fb_share_count)
