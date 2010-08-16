from datetime import timedelta
import unittest

from djangosanetesting.noseplugins import TestServerThread

from django.conf import settings
from django.core import mail
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client
from django.test.testcases import call_command

from poseur.fixtures import load_fixtures
from pytz import timezone
from paypal.standard.ipn.models import PayPalIPN
from selenium import selenium

from tiger.accounts.models import Site
from tiger.core.models import *
from tiger.core.tests.shrapnel import *
from tiger.fixtures import FakeOrder
from tiger.notify.tasks import DeliverOrderTask


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
    def setUp(self):
        if not Site.objects.count():
            load_fixtures('tiger.fixtures')
        site = Site.objects.all()[0]
        order_settings = site.ordersettings
        order_settings.receive_via = OrderSettings.RECEIPT_EMAIL
        order_settings.save()

    def create_paypal_order(self):
        FakeOrder.generate(count=1)
        order = Order.objects.all()[0]
        # no good way to hook into the PayPal interaction and stub it out,
        # so we start by saving an already processed object.  The ``verify``
        # method of ``PayPalIPN`` instances performs the postback, sets flags
        # on the instance, saves it to the database, and dispatches signals.
        # we're picking up with the call to ``save``.
        TEST_PAYPAL_TRANSACTION.update({
            'invoice': unicode(order.id)
        })
        paypal = PayPalIPN.objects.create(**TEST_PAYPAL_TRANSACTION)
        paypal.send_signals()
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


class OrderListTest(unittest.TestCase):
    def test_list_update(self):
        if not Site.objects.count():
            load_fixtures('tiger.fixtures')
        self.server_thread = TestServerThread('127.0.0.1', 8000)
        self.server_thread.start()
        self.server_thread.started.wait()
        if self.server_thread.error:
            raise self.server_thread.error
        self.selenium = selenium(
            'localhost',
            4444,
            '*firefox',
            'http://foo.takeouttiger.com:8000' 
        )
        self.selenium.start()
        self.selenium.open('/dashboard/login/')
        self.selenium.type('email', 'test@test.com')
        self.selenium.type('password', 'password')
        self.selenium.click("css=input[type='submit']")
        self.selenium.wait_for_page_to_load(2000)
        # create one already-read order
        FakeOrder.generate(count=1)
        order = Order.objects.all()[0]
        order.unread = True
        order.save()
        # assert that the one order is on list and does not have class unread
        self.selenium.open(reverse('dashboard_orders'))
        self.assertTrue(self.selenium.is_element_present("css=tr.unread"))
        self.assertFalse(self.selenium.is_element_present("css=tbody tr:nth-child(2)"))
        # click through on order
        self.selenium.click("css=tr:first-child a:first-child")
        self.selenium.wait_for_page_to_load(1000)
        # assert that no orders have class unread
        self.selenium.open(reverse('dashboard_orders'))
        self.assertFalse(self.selenium.is_element_present("css=tr.unread"))
        # create new order
        FakeOrder.generate(count=1)
        order = Order.objects.order_by('-id')[0]
        order.unread = True
        order.save()
        # wait for update -- page polls every minute
        time.sleep(60)
        # assert update
        self.assertTrue(self.selenium.is_element_present("css=tbody tr:nth-child(2)"))
        # assert that new order is on top
        # assert that new order has class unread
        self.assertTrue("unread" in self.selenium.get_attribute("css=tr#%d@class" % order.id))
