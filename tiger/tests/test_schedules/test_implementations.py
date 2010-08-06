from nose.tools import *

from django.core.urlresolvers import reverse
from django.test.client import Client

from tiger.accounts.models import Site, Schedule
from tiger.utils.hours import DOW_CHOICES 


def test_default_schedule():
    s = Site.objects.all()[0]

    # new sites should have no hours in one schedule
    assert_true(s.schedule_set.count() == 1)
    schedule = s.schedule_set.all()[0]
    assert_true(schedule.timeslot_set.count() == 0)

    # default schedule should be associated with the default location
    assert_true(schedule == s.location_set.all()[0].schedule)


# test application to location / online ordering restrictions
def test_orders_against_location_schedule():
    assert False

# test application to sections / online ordering restrictions
def test_orders_against_section_schedule():
    assert False

# test application to price point / online ordering restrictions
def test_orders_against_price_point_schedule():
    assert False
