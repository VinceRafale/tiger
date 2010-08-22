import math
from datetime import datetime, timedelta
from decimal import Decimal
import random

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client

from nose.tools import with_setup, raises
from poseur.fixtures import load_fixtures

from tiger.accounts.models import Site, TimeSlot, Schedule
from tiger.core.exceptions import *
from tiger.core.messages import *
from tiger.core.models import Section, Item, Variant
from tiger.utils.hours import DOW_CHOICES


def create_timeslots(schedule, dt, start_offset, stop_offset):
    for dow, display in DOW_CHOICES:
        TimeSlot.objects.create(
            dow=dow, schedule=schedule,
            start=(datetime.now() + timedelta(minutes=dt) - timedelta(minutes=start_offset)).time(),
            stop=(datetime.now() + timedelta(minutes=dt) + timedelta(minutes=stop_offset)).time()
        )


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
        order_settings.tax_rate = '6.25'
        order_settings.save()
        schedule, created = Schedule.objects.get_or_create(site=site, master=True)
        create_timeslots(schedule, dt, 30, 30)
    return _setup


def setup_section_timeslots(dt):
    def _setup():
        setup_timeslots(dt)()
        site = Site.objects.all()[0]
        section = Section.objects.all()[0]
        schedule = section.schedule
        if schedule is None:
            schedule = Schedule.objects.create(site=site)
        section.schedule = schedule
        section.save()
        create_timeslots(schedule, dt, 30, 0)
    return _setup


def setup_pricepoint_timeslots(dt):
    def _setup():
        setup_timeslots(dt)()
        site = Site.objects.all()[0]
        schedule = Schedule.objects.create(site=site)
        create_timeslots(schedule, dt, 30, 0)
        for item in site.item_set.all():
            item.variant_set.all().delete()
            item.archived = False
            item.out_of_stock = False
            item.save()
            # no schedule for one price point
            Variant.objects.create(description='large', item=item, price=Decimal('5.00'))
            v = Variant.objects.create(description='small', item=item, price=Decimal('3.00'), schedule=schedule)
    return _setup
            

def teardown_timeslots():
    for section in Section.objects.all():
        section.schedule = None
        section.save()
    Schedule.objects.all().delete()
        

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


@with_setup(setup_pricepoint_timeslots(10), teardown_timeslots)
def test_pricepoint_open():
    item = Item.objects.all()[0]
    assert item.variant_set.filter(description='small')[0].is_available


@with_setup(setup_pricepoint_timeslots(-10), teardown_timeslots)
@raises(PricePointNotAvailable)
def test_pricepoint_closed():
    item = Item.objects.all()[0]
    assert item.variant_set.filter(description='small')[0].is_available


def data_for_order_form(item, **variant_kwds):
    data = {'quantity': random.randint(1, 5)}
    if item.variant_set.count():
        data['variant'] = item.variant_set.filter(**variant_kwds)[0].id
    for sidegroup in item.sidedishgroup_set.all():
        if sidegroup.sidedish_set.count() > 1:
            data['side_%d' % sidegroup.id] = sidegroup.sidedish_set.order_by('?')[0].id 
    return data

class PricePointNotAvailableTestCase(TestCase):
    def setUp(self):
        setup_pricepoint_timeslots(-10)()
        self.client = Client(HTTP_HOST='foo.takeouttiger.com')
        self.client.get('/')
        self.item = Item.objects.order_by('?')[0]

    def test_scheduled_pricepoint_invalid(self):
        order_url = reverse('order_item', kwargs={'section': self.item.section.slug, 'item': self.item.slug})
        response = self.client.post(order_url, data_for_order_form(self.item, description='small'), follow=True)
        pricepoint = self.item.variant_set.filter(description='small')[0]
        pricepoint_error_msg = PRICEPOINT_NOT_AVAILABLE % (pricepoint.description, pricepoint.schedule.display)
        self.assertContains(response, pricepoint_error_msg)
        
    def test_nonscheduled_pricepoint_valid(self):
        order_url = reverse('order_item', kwargs={'section': self.item.section.slug, 'item': self.item.slug})
        response = self.client.post(order_url, data_for_order_form(self.item, description='large'), follow=True)
        pricepoint = self.item.variant_set.filter(description='large')[0]
        pricepoint_error_msg = PRICEPOINT_NOT_AVAILABLE % (pricepoint.description, '')
        self.assertNotContains(response, pricepoint_error_msg)


class ItemDisplayTestCase(TestCase):
    def setUp(self):
        setup_timeslots(0)()
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
