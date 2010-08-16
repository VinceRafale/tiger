import unittest
from tiger.core.tests.shrapnel import FakeSession, FakeCoupon
from tiger.core.middleware import Cart
from tiger.accounts.models import Site
from django.contrib.sessions.models import Session
from tiger.core.models import Coupon
from poseur.fixtures import load_fixtures


class CartTestCase(unittest.TestCase):
    cart = True

    def setUp(self):
        if not Site.objects.count():
            load_fixtures('tiger.fixtures')
        FakeSession.generate(count=1)
        self.session = Session.objects.all()[0]
        self.cart = Cart(self.session)
        FakeCoupon.generate(count=1)
        self.coupon = Coupon.objects.all()[0]
        
    def test_coupons(self):
        cart = self.cart
        self.assertFalse(cart.has_coupon)
        cart.add_coupon(self.coupon)
        self.assertTrue(cart.has_coupon)
        self.assertTrue(cart.coupon_display().startswith('Coupon'))  
        self.assertTrue(cart.coupon_display().endswith('off'))  
        cart.remove_coupon()
        self.assertFalse(cart.has_coupon)
        self.assertEquals(cart.coupon_display(), '')  
