import unittest
import random
from tiger.core.tests.shrapnel import FakeSession, FakeCoupon
from tiger.core.middleware import Cart
from tiger.accounts.models import Site
from django.contrib.sessions.models import Session
from tiger.core.forms import get_order_form
from tiger.core.models import Coupon, Item
from poseur.fixtures import load_fixtures


class CartTestCase(unittest.TestCase):
    cart = True

    @classmethod
    def setup_class(cls):
        if not Site.objects.count():
            load_fixtures('tiger.fixtures')
        FakeSession.generate(count=1)
        cls.session = Session.objects.all()[0]
        cls.cart = Cart(cls.session)
        FakeCoupon.generate(count=1)
        cls.coupon = Coupon.objects.all()[0]
        site = Site.objects.all()[0]
        order_settings = site.ordersettings
        order_settings.tax_rate = '6.25'
        order_settings.save()

    def random_order_form(self):
        no_variants = True
        while no_variants: 
            item = Item.objects.order_by('?')[0]
            if item.variant_set.count():
                break
        form_class = get_order_form(item)
        data = {'quantity': random.randint(1, 5)}
        if item.variant_set.count():
            data['variant'] = item.variant_set.order_by('?')[0].id
        for sidegroup in item.sidedishgroup_set.all():
            if sidegroup.sidedish_set.count() > 1:
                data['side_%d' % sidegroup.id] = sidegroup.sidedish_set.order_by('?')[0].id 
        bound_form = form_class(data)
        bound_form.full_clean()
        return item, bound_form
        
    def test_adding_to_total(self):
        cart = CartTestCase.cart
        self.assertEquals(cart.subtotal(), 0)
        self.assertEquals(cart.taxes(), 0)
        self.assertEquals(cart.total(), 0)
        cart.add(*self.random_order_form())
        self.assertNotEquals(cart.subtotal(), 0)
        self.assertNotEquals(cart.taxes(), 0)
        self.assertNotEquals(cart.total(), 0)
        self.assertEquals(cart.subtotal() - cart.discount(), cart.total())
        self.assertEquals(cart.total() + cart.taxes(), cart.total_plus_tax())
        
    def test_coupons(self):
        cart = CartTestCase.cart
        self.assertFalse(cart.has_coupon)
        cart.add_coupon(CartTestCase.coupon)
        self.assertTrue(cart.has_coupon)
        self.assertTrue(cart.coupon_display().startswith('Coupon'))  
        self.assertTrue(cart.coupon_display().endswith('off'))  
        cart.remove_coupon()
        self.assertFalse(cart.has_coupon)
        self.assertEquals(cart.coupon_display(), '')  
