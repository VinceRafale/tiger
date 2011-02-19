import random
import unittest

from django.conf import settings
from django.contrib.sessions.models import Session
from django.core import mail
from django.core.urlresolvers import reverse
from django.test.client import Client

from mock import Mock

from nose.exc import SkipTest

from faker.generators.utils import numerify
from paypal.standard.ipn.models import PayPalIPN
from pytz import timezone

from tiger.accounts.models import Site, Location
from tiger.core.forms import get_order_form
from tiger.core.middleware import Cart
from tiger.core.models import Item, Order, Coupon
from tiger.core.tests.shrapnel import TEST_PAYPAL_TRANSACTION, FakeSession, FakeCoupon
from tiger.fixtures import FakeOrder
from tiger.sales.models import Plan
from tiger.utils.test import TestCase



def data_for_order_form(item):
    data = {'quantity': random.randint(1, 5)}
    if item.variant_set.count():
        data['variant'] = item.variant_set.all()[0].id
    for sidegroup in item.sidedishgroup_set.all():
        if sidegroup.sidedish_set.count() > 1:
            data['side_%d' % sidegroup.id] = sidegroup.sidedish_set.order_by('?')[0].id 
    return data

def random_order_form():
    no_variants = True
    while no_variants: 
        item = Item.objects.order_by('?')[0]
        if item.variant_set.count():
            v = item.variant_set.all()[0]
            v.schedule = None
            v.save()
            break
    item.taxable = True
    item.save()
    form_class = get_order_form(item)
    data = data_for_order_form(item)
    bound_form = form_class(data, location=Location.objects.all()[0])
    bound_form.full_clean()
    return item, bound_form

def create_order():
    FakeOrder.generate(count=1)
    order = Order.objects.all()[0]
    session = Session.objects.all()[0]
    cart = Cart(session)
    cart.add(*random_order_form())
    order.cart = cart.contents
    order.save()
    return order
        
def deliver_paypal(order, **kwargs):
    TEST_PAYPAL_TRANSACTION.update({
        'invoice': unicode(order.id),
        'txn_id': numerify('########'),
        'payment_status': 'Completed'
    })
    TEST_PAYPAL_TRANSACTION.update(kwargs)
    paypal = PayPalIPN.objects.create(**TEST_PAYPAL_TRANSACTION)
    paypal.send_signals()


class CouponDisplayTestCase(unittest.TestCase):
    def setUp(self):
        self.site = Mock(Site())

    def test_dollar_display(self):
        dollar_coupon = Coupon(
            site=self.site, 
            short_code='', 
            discount_type=Coupon.DISCOUNT_DOLLARS,
            dollars_off='1.00'
        )
        self.assertEquals(dollar_coupon.discount, '$1.00')

    def test_percent_display(self):
        percent_coupon = Coupon(
            site=self.site, 
            short_code='', 
            discount_type=Coupon.DISCOUNT_PERCENT,
            percent_off=10
        )
        self.assertEquals(percent_coupon.discount, '10%')


class CouponUsageTestCase(TestCase):
    fixtures = ['plans.json']
    poseur_fixtures = 'tiger.fixtures'

    def setUp(self):
        self.site = Site.objects.all()[0]
        self.site.plan = Plan.objects.get(has_online_ordering=True)
        self.site.save()

    def test_add_remove_coupon(self):
        coupon = Coupon.objects.create(
            site=self.site, 
            short_code='TEST', 
            discount_type=Coupon.DISCOUNT_DOLLARS,
            dollars_off='1.00'
        )
        client = Client(HTTP_HOST='foo.takeouttiger.com')
        client.get(reverse('menu_home'))
        response = client.post(reverse('preview_order'), {'coupon_code': coupon.short_code}, follow=True)
        self.assertContains(response, 'Coupon TEST')
        response = client.get(reverse('clear_coupon'), follow=True)
        self.assertContains(response, 'Your coupon has been removed.')


class CartTestCase(TestCase):
    fixtures = ['plans.json']
    poseur_fixtures = 'tiger.fixtures'

    def setUp(self):
        FakeSession.generate(count=1)
        self.session = Session.objects.all()[0]
        self.cart = Cart(self.session)
        FakeCoupon.generate(count=1)
        self.coupon = Coupon.objects.all()[0]
        site = Site.objects.all()[0]
        location = site.location_set.all()[0]
        location.tax_rate = '6.25'
        location.save()

    def tearDown(self):
        Session.objects.all()[0].delete()

    def test_adding_to_total(self):
        cart = self.cart
        self.assertEquals(cart.subtotal(), 0)
        self.assertEquals(cart.taxes(), 0)
        self.assertEquals(cart.total(), 0)
        cart.add(*random_order_form())
        self.assertNotEquals(cart.subtotal(), 0)
        self.assertNotEquals(cart.taxes(), 0)
        self.assertNotEquals(cart.total(), 0)
        self.assertEquals(cart.subtotal() - cart.discount(), cart.total())
        self.assertEquals(cart.total() + cart.taxes(), cart.total_plus_tax())
        
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


class OrderPropertiesTest(TestCase):
    fixtures = ['plans.json']
    poseur_fixtures = 'tiger.fixtures'

    def test_display_hours(self):
        """Time that the order was placed should be localized to reflect the
        timezone selected by the restaurant.
        """
        site = Site.objects.all()[0]
        site.plan = Plan.objects.get(has_online_ordering=True)
        site.save()
        # site is using default timezone
        location = site.location_set.all()[0]
        self.assertEquals(settings.TIME_ZONE, location.timezone)
        FakeOrder.generate(count=1)
        order = Order.objects.all()[0]
        server_tz = timezone(settings.TIME_ZONE)
        server_timestamp = server_tz.localize(order.timestamp)
        self.assertEquals(order.localized_timestamp(), server_timestamp)
        order.delete()
        # set site timezone to PST
        location.timezone = 'US/Pacific'
        location.save()
        FakeOrder.generate(count=1)
        order = Order.objects.all()[0]
        server_tz = timezone(settings.TIME_ZONE)
        server_timestamp = server_tz.localize(order.timestamp)
        self.assertEquals(order.localized_timestamp(), server_timestamp)
        self.assertNotEquals(order.localized_timestamp().tzinfo, server_timestamp.tzinfo)


class PayPalOrderTest(TestCase):
    fixtures = ['plans.json']
    poseur_fixtures = 'tiger.fixtures'

    def setUp(self):
        site = Site.objects.all()[0]
        site.plan = Plan.objects.get(has_online_ordering=True)
        site.save()
        location = site.location_set.all()[0]
        location.receive_via = Location.RECEIPT_EMAIL
        location.tax_rate = '6.25'
        location.save()
        FakeSession.generate(count=1)

    def teardown(cls):
        Session.objects.all()[0].delete()

    def create_paypal_order(self, **kwargs):
        # no good way to hook into the PayPal interaction and stub it out,
        # so we start by saving an already processed object.  The ``verify``
        # method of ``PayPalIPN`` instances performs the postback, sets flags
        # on the instance, saves it to the database, and dispatches signals.
        # we're picking up with the call to ``save``.
        order = create_order()
        deliver_paypal(order, **kwargs)
        return order

    def test_paypal_transaction(self):
        order = self.create_paypal_order()
        order = Order.objects.get(id=order.id)
        # assert that Order is flagged as paid
        self.assertEquals(order.status, Order.STATUS_PAID)
        # assert that e-mail is sent
        self.assertEquals(len(mail.outbox), 1)

    def test_paypal_email_display(self):
        """Ensure that payer e-mail is displayed on order detail page if order
        was paid for via PayPal.
        """
        order = self.create_paypal_order()
        client = Client(HTTP_HOST='foo.takeouttiger.com')
        self.assertTrue(client.login(email='test@test.com', password='password', site=Site.objects.all()[0]))
        response = client.get(reverse('order_detail', args=[order.id]))
        self.assertContains(response, PayPalIPN.objects.all()[0].payer_email)
        self.assertContains(response, 'Paid online')

    def test_paypal_refunded(self):
        order = self.create_paypal_order()
        order = Order.objects.get(id=order.id)
        self.create_paypal_order(invoice=unicode(order.id), payment_status='Refunded')
        client = Client(HTTP_HOST='foo.takeouttiger.com')
        self.assertTrue(client.login(email='test@test.com', password='password', site=Site.objects.all()[0]))
        response = client.get(reverse('order_detail', args=[order.id]))
        self.assertContains(response, 'Refunded')

    def test_payment_pending(self):
        client = Client(HTTP_HOST='foo.takeouttiger.com')
        self.assertTrue(client.login(email='test@test.com', password='password', site=Site.objects.all()[0]))
        order = create_order()
        order.status = Order.STATUS_PENDING
        order.save()
        response = client.get(reverse('order_detail', args=[order.id]))
        self.assertContains(response, 'Payment pending')
        deliver_paypal(order)
        response = client.get(reverse('order_detail', args=[order.id]))
        self.assertNotContains(response, 'Payment pending')
        self.assertContains(response, 'Paid online')


class OrderListTest(TestCase):
    def test_jonathan_has_replaced_this_with_a_stubbed_javascript_test(self):
        raise SkipTest


class OrderScreensAvailabilityTestCase(TestCase):
    fixtures = ['plans.json']
    poseur_fixtures = 'tiger.fixtures'

    def setUp(self):
        self.site = Site.objects.all()[0]
        self.client = Client(HTTP_HOST='foo.takeouttiger.com')
        urls = map(reverse, [
            'preview_order',
            'send_order',
            'order_success',
            'payment_paypal',
            'payment_authnet'])
        item = Item.objects.all()[0]
        urls.append(reverse('order_item', kwargs={
            'section_id': item.section.id,
            'section_slug': item.section.slug,
            'item_id': item.id,
            'item_slug': item.slug
        }))
        self.ordering_urls = urls

    def test_site_with_online_ordering_has_ordering_screens(self):
        self.site.plan = Plan.objects.get(has_online_ordering=True)
        self.site.save()
        # hit menu screen just to set cookie
        self.client.get(reverse('menu_home'))
        for url in self.ordering_urls:
            response = self.client.get(url)
            self.assertNotEquals(response.status_code, 404)

    def test_site_without_online_ordering_has_no_ordering_screens(self):
        self.site.plan = Plan.objects.filter(has_online_ordering=False)[0]
        self.site.save()
        # hit menu screen just to set cookie
        self.client.get(reverse('menu_home'))
        for url in self.ordering_urls:
            response = self.client.get(url)
            self.assertEquals(response.status_code, 404)
