from django.contrib.auth.models import User
from django.conf import settings
from django.core import mail
from django.core.urlresolvers import reverse
from django.http import Http404
from django.test.client import Client, RequestFactory

from mock import Mock, patch
from poseur.fixtures import load_fixtures

from tiger import reseller_settings
from tiger.accounts.models import Site
from tiger.accounts.views import domain_check
from tiger.sales.exceptions import PaymentGatewayError, SiteManagementError
from tiger.sales.forms import CreateResellerAccountForm, CreateSiteForm
from tiger.sales.models import Account, Plan, Invoice
from tiger.utils.test import TestCase


class DomainCheckTestCase(TestCase):
    poseur_fixtures = 'tiger.sales.fixtures.accounts'
    
    def setUp(self):
        self.client = Client(HTTP_HOST='foo.takeouttiger.com')
        self.site = Site.objects.all()[0]
        self.factory = RequestFactory()

    def test_available_domain_check_non_ajax(self):
        request = self.factory.post('/domain-check/', {})
        self.assertRaises(Http404, domain_check, request)

    def test_available_domain_check(self):
        request = self.factory.post('/domain-check/', {'subdomain': 'bar'}, 
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        response = domain_check(request)
        self.assertEqual(response.content, '{"available": true}')

    def test_unavailable_domain_check(self):
        request = self.factory.post('/domain-check/', {'subdomain': 'foo'}, 
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        response = domain_check(request)
        self.assertEqual(response.content, '{"available": false}')


class NewSiteFormTestCase(TestCase):
    fixtures = ['plans.json']
    poseur_fixtures = 'tiger.sales.fixtures.accounts'
    
    def setUp(self):
        self.client = Client(HTTP_HOST='bar.takeouttiger.com')
        self.account = Account.objects.all()[0]
        self.factory = RequestFactory()
        self.data = {
            'email': 'restaurant@restaurant.com',
            'name': 'Restaurant',
            'subdomain': 'bar'
        }
        one, two, three = Plan.objects.all()
        one.account = two.account = self.account
        one.save()
        two.save()
        self.valid_plan = one
        self.invalid_plan = three

    def test_plan_choices_restricted_to_account(self):
        data = self.data.copy()
        data['plan'] = self.invalid_plan.id
        form = CreateSiteForm(data, account=self.account)
        self.assertFalse(form.is_valid())
        self.assertTrue(form._errors.has_key('plan'))

    def test_invalid_payment_info_invalidates_form(self):
        data = self.data.copy()
        data['plan'] = self.valid_plan.id
        Invoice.objects.create(account=self.account, status=Invoice.STATUS_FAILED)
        form = CreateSiteForm(data, account=self.account)
        self.assertTrue(form.is_bound)
        self.assertFalse(form.is_valid())
        self.assertTrue('Your most recent invoice could not be processed.  Please update your billing information before creating more sites.' in form.non_field_errors())

    def test_valid_form_creates_site_and_user(self):
        data = self.data.copy()
        data['plan'] = self.valid_plan.id
        form = CreateSiteForm(data, account=self.account)
        site = form.save()
        self.assertTrue(self.client.login(email=data['email'], password=site.user.username, site=site))
        self.assertEquals(self.client.get('/').status_code, 200)


class ResellerSignupFormTestCase(TestCase):
    urls = 'tiger.reseller_urls'
    poseur_fixtures = 'tiger.sales.fixtures.accounts'
    patch_settings = {
        'tiger.reseller_settings': (
            'AUTHENTICATION_BACKENDS',
            'MIDDLEWARE_CLASSES',
            'INSTALLED_APPS',
        )
    }
    
    def setUp(self):
        self.client = Client(HTTP_HOST='foo.takeouttiger.com')
        self.account = Account.objects.all()[0]
        self.factory = RequestFactory()
        self.data = {
            'email': 'new@new.com',
            'password1': 'password',
            'password2': 'password',
            'cc_number': '1',
            'first_name': 'First',
            'last_name': 'Last',
            'zip': '11111',
            'month': '3',
            'year': '2012',
        }

    def test_invalid_credit_card_displays_errors(self):
        with patch.object(CreateResellerAccountForm, 'create_payment_profile') as mock_method:
            mock_method.side_effect = PaymentGatewayError()
            form = CreateResellerAccountForm(self.data)
            self.assertFalse(form.is_valid())
            self.assertTrue(form.create_payment_profile.called)
            self.assertTrue('Unable to process your credit card.' in form.non_field_errors())

    def test_valid_form_creates_manager_account(self):
        with patch.object(CreateResellerAccountForm, 'create_payment_profile') as mock_method:
            mock_method.return_value = ['foo', 'bar']
            form = CreateResellerAccountForm(self.data)
            form.full_clean()
            self.assertTrue(form.create_payment_profile.called)
            account = form.save()
            self.assertEquals(account.customer_id, 'foo')
            self.assertEquals(account.subscription_id, 'bar')
            self.assertTrue(account.manager)
            self.assertEquals(len(mail.outbox), 1)
            self.assertTrue(self.client.login(email=account.user.email, password='password'))
