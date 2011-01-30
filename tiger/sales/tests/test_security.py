from datetime import date, timedelta

from dateutil.relativedelta import *

from django.contrib.auth.models import User
from django.conf import settings
from django.core import mail
from django.core.urlresolvers import reverse
from django.test.client import Client

from poseur.fixtures import load_fixtures

from tiger.utils.test import TestCase
from tiger import reseller_settings
from tiger.accounts.models import Site


class ManagedAccountSecurityTestCase(TestCase):
    poseur_fixtures = 'tiger.sales.fixtures.accounts'
    
    def setUp(self):
        self.client = Client(HTTP_HOST='foo.takeouttiger.com')
        self.site = Site.objects.all()[0]
        user = User.objects.create_user('foo', 'foo@foo.com', password='password')
        user.is_superuser = True
        user.save()
        self.site.user = user
        self.site.save()

    def test_account_manager_can_log_in(self):
        user = self.site.account.user
        self.assertTrue(self.client.login(email=user.email, password='password', site=self.site))

    def test_site_manager_can_log_in(self):
        user = self.site.user
        self.assertTrue(self.client.login(email=user.email, password='password', site=self.site))

    def test_account_manager_for_different_site_cannot_log_in(self):
        account = Account.objects.exclude(id=self.site.account.id)[0]
        user = User.objects.create_user('foo', 'foo@foo.com', password='password')
        self.assertFalse(self.client.login(email=account.user.email, password='password', site=self.site))


class ManagedAccountSecurityTestCase(TestCase):
    urls = 'tiger.reseller_urls'
    poseur_fixtures = 'tiger.sales.fixtures.accounts'

    def setUp(self):
        self.site = Site.objects.all()[0]
        self.site.user = User.objects.create_user('foo', 'foo@foo.com', password='password')
        self.site.save()
        account = self.site.account
        account.manager = True
        account.save()
        self.client = Client()
        self.old_backends = settings.AUTHENTICATION_BACKENDS
        self.middleware = settings.MIDDLEWARE_CLASSES
        self.apps = settings.INSTALLED_APPS
        settings.AUTHENTICATION_BACKENDS = reseller_settings.AUTHENTICATION_BACKENDS
        settings.MIDDLEWARE_CLASSES = reseller_settings.MIDDLEWARE_CLASSES
        settings.MIDDLEWARE_CLASSES = reseller_settings.MIDDLEWARE_CLASSES
        settings.INSTALLED_APPS = reseller_settings.INSTALLED_APPS

    def tearDown(self):
        settings.AUTHENTICATION_BACKENDS = self.old_backends
        settings.MIDDLEWARE_CLASSES = self.middleware
        settings.INSTALLED_APPS = self.apps

    def test_nonexistent_user(self):
        self.assertFalse(self.client.login(email='fakey.mcfakerson@phishfood.com', password='password'))

    def test_account_manager_can_log_into_reseller_site(self):
        user = self.site.account.user
        self.assertTrue(self.client.login(email=user.email, password='password'))

    def test_managed_site_user_cannot_log_into_reseller_site(self):
        user = self.site.user
        self.assertFalse(self.client.login(email=user.email, password='password'))
