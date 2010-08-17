from datetime import timedelta
import random
import unittest

from django.conf import settings
from django.contrib.sessions.models import Session
from django.core import mail
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client
from django.test.testcases import call_command

from djangosanetesting.noseplugins import TestServerThread
from faker.generators.utils import numerify
from paypal.standard.ipn.models import PayPalIPN
from poseur.fixtures import load_fixtures
from poseur.fixtures import load_fixtures
from pytz import timezone
from selenium import selenium

from tiger.accounts.models import Site
from tiger.core.forms import get_order_form
from tiger.core.middleware import Cart
from tiger.core.models import *
from tiger.core.tests.shrapnel import *
from tiger.fixtures import FakeOrder
from tiger.notify.tasks import DeliverOrderTask


def random_order_form():
    no_variants = True
    while no_variants: 
        item = Item.objects.order_by('?')[0]
        if item.variant_set.count():
            break
    item.taxable = True
    item.save()
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

    @classmethod
    def teardown_class(cls):
        Session.objects.all()[0].delete()

    def test_adding_to_total(self):
        cart = CartTestCase.cart
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
        cart = CartTestCase.cart
        self.assertFalse(cart.has_coupon)
        cart.add_coupon(CartTestCase.coupon)
        self.assertTrue(cart.has_coupon)
        self.assertTrue(cart.coupon_display().startswith('Coupon'))  
        self.assertTrue(cart.coupon_display().endswith('off'))  
        cart.remove_coupon()
        self.assertFalse(cart.has_coupon)
        self.assertEquals(cart.coupon_display(), '')  


class OrderPropertiesTest(TestCase):
    def setUp(self):
        if not Site.objects.count():
            load_fixtures('tiger.fixtures')

    def test_display_hours(self):
        """Time that the order was placed should be localized to reflect the
        timezone selected by the restaurant.
        """
        site = Site.objects.all()[0]
        # site is using default timezone
        self.assertEquals(settings.TIME_ZONE, site.timezone)
        FakeOrder.generate(count=1)
        order = Order.objects.all()[0]
        server_tz = timezone(settings.TIME_ZONE)
        server_timestamp = server_tz.localize(order.timestamp)
        self.assertEquals(order.localized_timestamp(), server_timestamp)
        order.delete()
        # set site timezone to PST
        site.timezone = 'US/Pacific'
        site.save()
        FakeOrder.generate(count=1)
        order = Order.objects.all()[0]
        server_tz = timezone(settings.TIME_ZONE)
        server_timestamp = server_tz.localize(order.timestamp)
        self.assertEquals(order.localized_timestamp(), server_timestamp)
        self.assertNotEquals(order.localized_timestamp().tzinfo, server_timestamp.tzinfo)


class PayPalOrderTest(TestCase):
    paypal = True

    def setUp(self):
        if not Site.objects.count():
            load_fixtures('tiger.fixtures')
        site = Site.objects.all()[0]
        order_settings = site.ordersettings
        order_settings.receive_via = OrderSettings.RECEIPT_EMAIL
        order_settings.tax_rate = '6.25'
        order_settings.save()

    @classmethod
    def setup_class(cls):
        FakeSession.generate(count=1)

    @classmethod
    def teardown_class(cls):
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



class OrderListTest(unittest.TestCase):
    def setUp(self):
        if not Site.objects.count():
            load_fixtures('tiger.fixtures')
        self.server_thread = TestServerThread('127.0.0.1', 8000)
        self.server_thread.start()
        self.server_thread.started.wait()
        if self.server_thread.error:
            raise self.server_thread.error
        self.sel = selenium(
            'localhost',
            4444,
            '*firefox',
            'http://foo.takeouttiger.com:8000' 
        )
        self.sel.start()
        self.sel.open('/dashboard/login/')
        self.sel.type('email', 'test@test.com')
        self.sel.type('password', 'password')
        self.sel.click("css=input[type='submit']")
        self.sel.wait_for_page_to_load(2000)

    def tearDown(self):
        self.sel.close()
        self.server_thread.join()

    def test_list_update(self):
        # create one already-read order
        FakeOrder.generate(count=1)
        order = Order.objects.all()[0]
        order.unread = True
        order.save()
        # assert that the one order is on list and does not have class unread
        self.sel.open(reverse('dashboard_orders'))
        self.assertTrue(self.sel.is_element_present("css=tr.unread"))
        self.assertFalse(self.sel.is_element_present("css=tbody tr:nth-child(2)"))
        # click through on order
        self.sel.click("css=tr:first-child a:first-child")
        self.sel.wait_for_page_to_load(1000)
        # assert that no orders have class unread
        self.sel.open(reverse('dashboard_orders'))
        self.assertFalse(self.sel.is_element_present("css=tr.unread"))
        # create new order
        FakeOrder.generate(count=1)
        order = Order.objects.order_by('-id')[0]
        order.unread = True
        order.save()
        # wait for update -- page polls every minute
        time.sleep(60)
        # assert update
        self.assertTrue(self.sel.is_element_present("css=tbody tr:nth-child(2)"))
        # assert that new order is on top
        # assert that new order has class unread
        self.assertTrue("unread" in self.sel.get_attribute("css=tr#%d@class" % order.id))
