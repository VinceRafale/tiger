from datetime import date, timedelta

from dateutil.relativedelta import *

from django.core import mail
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.test.client import Client

from poseur.fixtures import load_fixtures

from tiger.accounts.models import Site
from tiger.notify.forms import PublishForm
from tiger.notify.models import Fax, Social
from tiger.sales.exceptions import PaymentGatewayError, SiteManagementError
from tiger.sales.models import Invoice, Plan
from tiger.sms.models import SMS, SmsSubscriber
from tiger.utils.test import TestCase


class BillingTestCase(TestCase):
    billing = True
    fixtures = ['plans.json']
    poseur_fixtures = 'tiger.fixtures'

    def setUp(self):
        self.site = Site.objects.all()[0]
        self.site.plan = Plan.objects.all()[0]
        self.site.managed = False
        self.site.save()
        self.client = Client(HTTP_HOST='foo.takeouttiger.com')

    def tearDown(self):
        Invoice.objects.all().delete()
        site = self.site
        sms = site.sms
        sms.sms_number = None
        sms.save()

    def test_first_partial_month_is_billed_prorated(self):
        """If the signup date for a site is in the past month, the first invoice
        generated should contain a monthly charge that is approximately the monthly
        cost multiplied by (days in month - signup day) / days in month.
        """
        site = self.site
        current_month = date.today().replace(day=1)
        last_day_of_previous_month = current_month - timedelta(days=1)
        site.signup_date = date.today()
        site.save()
        invoice = site.create_invoice()
        self.assertTrue(invoice.monthly_fee < site.plan.monthly_cost / 2)

    def test_first_full_month_is_billed_in_full(self):
        """If the signup date for a site is more than one month in the past, the
        first invoice generated should contain a monthly charge full the full cost
        of the plan.
        """
        site = self.site
        current_month = date.today().replace(day=1)
        last_day_of_previous_month = current_month - timedelta(days=1)
        site.signup_date = last_day_of_previous_month - timedelta(days=40)
        site.save()
        invoice = site.create_invoice()
        self.assertEqual(invoice.monthly_fee, site.plan.monthly_cost)

    def test_fax_is_billed(self):
        site = self.site
        current_month = date.today().replace(day=1)
        last_day_of_previous_month = current_month - timedelta(days=1)
        site.signup_date = last_day_of_previous_month - timedelta(days=40)
        for i in range(5):
            Fax.objects.create(
                site=site,
                page_count=2,
                transaction='000',
                timestamp=date.today()+relativedelta(months=-2),
                logged=True
            )
        for i in range(5):
            Fax.objects.create(
                site=site,
                page_count=2,
                transaction='000',
                timestamp=date.today()+relativedelta(months=-1),
                logged=False
            )
        invoice = site.create_invoice()
        fax_cost = site.plan.fax_page_cost * 10
        self.assertEqual(fax_cost, invoice.fax_charges)
        self.assertEqual(fax_cost + site.plan.monthly_cost, invoice.total)

    def test_sms_monthly_charge_is_billed(self):
        site = self.site
        sms = site.sms
        sms.sms_number = '14135334095'
        sms.save()
        current_month = date.today().replace(day=1)
        last_day_of_previous_month = current_month - timedelta(days=1)
        site.signup_date = last_day_of_previous_month - timedelta(days=40)
        invoice = site.create_invoice()
        sms_number_cost = site.plan.sms_number_cost
        self.assertEqual(sms_number_cost, invoice.sms_number_charges)
        self.assertEqual(sms_number_cost + site.plan.monthly_cost, invoice.total)

    def test_sms_usage_charges_are_billed(self):
        site = self.site
        current_month = date.today().replace(day=1)
        last_day_of_previous_month = current_month - timedelta(days=1)
        site.signup_date = last_day_of_previous_month - timedelta(days=40)
        subscriber = SmsSubscriber.objects.create(settings=site.sms)
        for i in range(5):
            SMS.objects.create(
                settings=site.sms,
                subscriber=subscriber,
                sid='000',
                body='text',
                read=False,
                timestamp=date.today()+relativedelta(months=-2),
                logged=False
            )
        invoice = site.create_invoice()
        sms_cost = site.plan.sms_cost * 5
        self.assertEqual(sms_cost, invoice.sms_usage_charges)
        self.assertEqual(sms_cost + site.plan.monthly_cost, invoice.total)

    def test_successful_cc_closes_invoice(self):
        """If the invoice is successfully charged to the accounts credit card,
        a receipt should be e-mailed and the invoice status should be marked as
        successful.
        """
        #TODO: mock invoice.send_to_gateway to automatically succeed
        site = self.site
        invoice = site.create_invoice()
        invoice.send_to_gateway = lambda: '0101010101010101'
        invoice.charge()
        self.assertEqual(invoice.status, Invoice.STATUS_SUCCESS)
        self.assertEquals(len(mail.outbox), 1)
        self.client.login(email='test@test.com', password='password', site=Site.objects.all()[0])
        response = self.client.get(reverse('sms_home'), follow=True, SERVER_NAME='foo.takeouttiger.com')
        self.assertEqual(response.status_code, 200)

    def test_failed_cc_keeps_invoice_open(self):
        """If charging an invoice to a credit card fails, send a warning e-mail and
        mark the invoice as failed.  Additionally, suspend use of SMS/fax until
        resolved.
        """
        site = self.site
        invoice = site.create_invoice()
        def kill_payment():
            raise PaymentGatewayError
        invoice.send_to_gateway = kill_payment
        invoice.charge()
        self.assertEqual(invoice.status, Invoice.STATUS_FAILED)
        self.assertEquals(len(mail.outbox), 1)
        self.client.login(email='test@test.com', password='password', site=Site.objects.all()[0])
        response = self.client.post(reverse('dashboard_publish_new'), {
            'title': 'test',
            'fax': True
        })
        self.assertFormError(response, 'form', 'fax', 'Faxing charges are 10 cents per page delivered.  You do not have a valid credit card on file.  Please update your payment information.')


class IndieCustomerTestCase(TestCase):
    billing = True
    fixtures = ['plans.json']
    poseur_fixtures = 'tiger.fixtures'

    def setUp(self):
        self.site = Site.objects.all()[0]
        self.site.plan = Plan.objects.all()[0]
        self.site.managed = False
        self.site.save()
        self.client = Client(HTTP_HOST='foo.takeouttiger.com')
        from django.conf import settings
        settings.DEBUG = True

    def tearDown(self):
        Invoice.objects.all().delete()
        site = self.site
        sms = site.sms
        sms.sms_number = None
        sms.save()

    def test_sms_suspended_indie(self):
        site = self.site
        invoice = site.create_invoice()
        def kill_payment():
            raise PaymentGatewayError
        invoice.send_to_gateway = kill_payment
        invoice.charge()
        self.client.login(email='test@test.com', password='password', site=Site.objects.all()[0])
        response = self.client.get(reverse('sms_home'), follow=True, SERVER_NAME='foo.takeouttiger.com')
        self.assertRedirects(response, 'http://foo.takeouttiger.com' + reverse('update_cc'))
        self.assertContains(response, 'Your account has been suspended')

    def test_indie_customer_has_invoice_tab(self):
        self.client.login(email='test@test.com', password='password', site=Site.objects.all()[0])
        for url in ('update_cc', 'billing_history', 'cancel',):
            response = self.client.get(reverse(url), follow=True, SERVER_NAME='foo.takeouttiger.com')
            self.assertEqual(200, response.status_code)


class ManagedCustomerTestCase(TestCase):
    billing = True
    fixtures = ['plans.json']
    poseur_fixtures = 'tiger.fixtures'

    def setUp(self):
        self.site = Site.objects.all()[0]
        self.site.plan = Plan.objects.all()[0]
        self.site.managed = True
        self.site.save()
        self.client = Client(HTTP_HOST='foo.takeouttiger.com')

    def tearDown(self):
        Invoice.objects.all().delete()
        site = self.site
        sms = site.sms
        sms.sms_number = None
        sms.save()

    def test_managed_site_cannot_create_invoice(self):
        """If the site is a direct customer of Takeout Tiger, the associated
        account gets its own invoice.
        """
        self.assertRaises(SiteManagementError, self.site.create_invoice)

    def test_managed_customer_is_billed_to_managing_account(self):
        """If the site is managed by a reseller, the site's invoice will be a
        subinvoice of an invoice for all the sites managed by the reseller.
        """
        invoice = self.site.account.create_invoice()
        self.assertEqual(self.site, invoice.subinvoice_set.all()[0].site)
        self.assertEqual(None, invoice.site)

    def test_sms_suspended_managed(self):
        site = self.site
        invoice = site.account.create_invoice()
        def kill_payment():
            raise PaymentGatewayError
        invoice.send_to_gateway = kill_payment
        invoice.charge()
        # instrument cache for facebook fragment
        CACHE_KEY = Social.FACEBOOK_CACHE_KEY  % site.social.id
        cache.set(CACHE_KEY, '')
        self.client.login(email='test@test.com', password='password', site=Site.objects.all()[0])
        response = self.client.get(reverse('sms_home'), follow=True, SERVER_NAME='foo.takeouttiger.com')
        self.assertRedirects(response, 'http://foo.takeouttiger.com' + reverse('dashboard_marketing'))
        self.assertContains(response, 'Your account has been suspended')

    def test_managed_site_has_no_invoice_tab(self):
        self.client.login(email='test@test.com', password='password', site=Site.objects.all()[0])
        for url in ('update_cc', 'billing_history', 'cancel',):
            response = self.client.get(reverse(url), follow=True, SERVER_NAME='foo.takeouttiger.com')
            self.assertEqual(404, response.status_code)

    def test_no_online_ordering_plan(self):
        """Plans without online ordering cannot access Orders tab screens"""
        self.site.plan = Plan.objects.create(name='no orders', has_online_ordering=False)
        self.site.save()
        self.client.login(email='test@test.com', password='password', site=Site.objects.all()[0])
        for url in ('dashboard_orders', 'order_options', 'order_payment', 'order_messages', 'get_new_orders',):
            response = self.client.get(reverse(url), follow=True, SERVER_NAME='foo.takeouttiger.com')
            self.assertEqual(404, response.status_code)

    def test_online_ordering_plan(self):
        """Plans with online ordering can access Orders tab screens"""
        self.site.plan = Plan.objects.create(name='no orders', has_online_ordering=True)
        self.site.save()
        self.client.login(email='test@test.com', password='password', site=Site.objects.all()[0])
        for url in ('dashboard_orders', 'order_options', 'order_payment', 'order_messages', 'get_new_orders',):
            response = self.client.get(reverse(url), follow=True, SERVER_NAME='foo.takeouttiger.com')
            self.assertEqual(200, response.status_code)
