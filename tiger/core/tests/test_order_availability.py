import math
from datetime import datetime, timedelta

from django.test import TestCase
from django.test.client import Client

from nose.tools import with_setup, raises
from poseur.fixtures import load_fixtures

from tiger.accounts.models import Site, TimeSlot
from tiger.core.exceptions import *
from tiger.core.messages import *
from tiger.core.models import Section, Item, Variant
from tiger.utils.hours import DOW_CHOICES


def setup_timeslots(dt):
    """Returns a callable to be passed to ``with_setup`` that generates time
    slots with offset of ``dt`` minutes.
    """
    def _setup():
        if not Site.objects.count():
            load_fixtures('tiger.fixtures')
        site = Site.objects.all()[0]
        site.enable_orders = True
        site.save()
        order_settings = site.ordersettings
        order_settings.eod_buffer = 15
        order_settings.save()

        for dow, display in DOW_CHOICES:
            TimeSlot.objects.create(
                dow=dow, site=site,
                start=(datetime.now() + timedelta(minutes=dt) - timedelta(minutes=30)).time(),
                stop=(datetime.now() + timedelta(minutes=dt) + timedelta(minutes=30)).time()
            )
    return _setup


def setup_section_timeslots(dt):
    def _setup():
        setup_timeslots(dt)()
        site = Site.objects.all()[0]
        section = Section.objects.all()[0]
        for dow, display in DOW_CHOICES:
            TimeSlot.objects.create(
                dow=dow, site=site, section=section,
                start=(datetime.now() + timedelta(minutes=dt) - timedelta(minutes=30)).time(),
                stop=(datetime.now() + timedelta(minutes=dt)).time()
            )
    return _setup


def teardown_timeslots():
    TimeSlot.objects.all().delete()
        

@with_setup(setup_timeslots(0), teardown_timeslots)
@raises(NoOnlineOrders)
def test_online_ordering_disabled():
    site = Site.objects.all()[0]
    site.enable_orders = False
    assert site.is_open


@with_setup(setup_timeslots(0), teardown_timeslots)
def test_online_ordering_enabled():
    site = Site.objects.all()[0]
    site.enable_orders = True
    site.save()
    assert site.is_open


@with_setup(setup_timeslots(90), teardown_timeslots)
@raises(RestaurantNotOpen)
def test_restaurant_is_closed_early():
    site = Site.objects.all()[0]
    assert site.is_open


@with_setup(setup_timeslots(-90), teardown_timeslots)
@raises(RestaurantNotOpen)
def test_restaurant_is_closed_late():
    site = Site.objects.all()[0]
    assert site.is_open


@with_setup(setup_timeslots(-20), teardown_timeslots)
@raises(ClosingTimeBufferError)
def test_within_closing_buffer():
    site = Site.objects.all()[0]
    assert site.is_open


@with_setup(setup_section_timeslots(10), teardown_timeslots)
def test_section_open():
    section = Section.objects.all()[0]
    assert section.is_available


@with_setup(setup_section_timeslots(-10), teardown_timeslots)
@raises(SectionNotAvailable)
def test_section_closed():
    section = Section.objects.all()[0]
    assert section.is_available


@with_setup(setup_section_timeslots(-10), teardown_timeslots)
@raises(SectionNotAvailable)
def test_item_with_section_closed():
    item = Item.objects.all()[0]
    assert item.is_available


@raises(ItemNotAvailable)
def test_item_archived():
    item = Item.objects.all()[0]
    item.archived = True
    assert item.is_available


@raises(ItemNotAvailable)
def test_item_out_of_stock():
    item = Item.objects.all()[0]
    item.out_of_stock = True
    assert item.is_available


def test_item_available():
    item = Item.objects.all()[0]
    item.out_of_stock = False
    item.archived = False
    assert item.is_available


class ItemDisplayTestCase(TestCase):
    def setUp(self):
        if not Site.objects.count():
            load_fixtures('tiger.fixtures')
        self.client = Client(HTTP_HOST='foo.takeouttiger.com')
        self.client.get('/')
        self.item = Variant.objects.all()[0].item
        self.item.update_price()

    def test_available(self):
        self.item.archived = self.item.out_of_stock = False
        self.item.save()
        response = self.client.get(self.item.get_absolute_url())
        self.assertNotContains(response, ITEM_NOT_AVAILABLE % self.item.name)

    def test_archived(self):
        self.item.archived = True
        self.item.save()
        response = self.client.get(self.item.get_absolute_url())
        self.assertContains(response, ITEM_NOT_AVAILABLE % self.item.name)

    def test_out_of_stock(self):
        self.item.out_of_stock = True
        self.item.save()
        response = self.client.get(self.item.get_absolute_url())
        self.assertContains(response, ITEM_NOT_AVAILABLE % self.item.name)
