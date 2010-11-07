from datetime import timedelta

from django.core.urlresolvers import reverse
from django.conf import settings
from django.test import TestCase
from django.test.client import Client

from nose.tools import *
from poseur.fixtures import load_fixtures

from tiger.accounts.models import Site
from tiger.track.models import Hit, Session


class TrackingTestCase(TestCase):
    def setUp(self):
        if not Site.objects.count():
            load_fixtures('tiger.fixtures')
        self.client = Client(HTTP_HOST='foo.takeouttiger.com')

    def test_no_dashboard_hits(self):
        self.client.get('/dashboard/menu/')
        self.assertEquals(0, Hit.objects.count())
        self.assertEquals(0, Session.objects.count())

    def test_new_session_no_referrer(self):
        self.client.get('/')
        try:
            session = Session.objects.order_by('-id')[0]
        except Session.DoesNotExist:
            self.fail()
        self.assertEquals(1, session.hit_set.count())

    def test_new_session_offsite_referrer(self):
        self.client.get('/', HTTP_REFERER='www.google.com')
        try:
            session = Session.objects.order_by('-id')[0]
        except Session.DoesNotExist:
            self.fail()
        self.assertEquals(1, session.hit_set.count())
        hit = session.hit_set.all()[0]
        self.assertEquals('www.google.com', hit.referrer)

    def test_new_session_stale_session(self):
        self.client.get('/')
        session = Session.objects.order_by('-id')[0]
        hit = session.hit_set.all()[0]
        hit.timestamp = hit.timestamp - timedelta(minutes=10)
        hit.save()
        self.client.get('/')
        new_session = Session.objects.order_by('-id')[0]
        self.assertEquals(session.session, new_session.session)
        self.assertNotEquals(session, new_session)

    def test_current_session(self):
        self.client.get('/')
        self.client.get('/')
        session = Session.objects.order_by('-id')[0]
        self.assertEquals(2, session.hit_set.count())

    def test_hit_numbering(self):
        paths = ('/', '/menu/', '/find-us/')
        for path in paths:
            self.client.get(path)
        session = Session.objects.order_by('-id')[0]
        for i, p in enumerate(paths):
            hit = session.hit_set.get(path=p)
            self.assertEquals(i, hit.hit_number)
