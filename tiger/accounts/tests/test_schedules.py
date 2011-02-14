from datetime import time, datetime

from django.core.urlresolvers import reverse
from django.test.client import Client

from nose.tools import *

from tiger.accounts.forms import TimeSlotForm
from tiger.accounts.models import Site, Schedule, TimeSlot, Location
from tiger.utils.hours import *
from tiger.utils.test import TestCase


class AddEditScheduleTest(TestCase):
    poseur_fixtures = 'tiger.fixtures'

    # edit schedule
    def test_schedule_dashboard(self):
        client = Client(HTTP_HOST='foo.takeouttiger.com', SERVER_NAME='foo.takeouttiger.com')
        self.assertTrue(client.login(email='test@test.com', password='password', site=Site.objects.all()[0]))
        # create a new schedule
        post_data = {}
        [
            post_data.update({'%d-start' % dow: '09:00 AM',  '%d-stop' % dow: '09:00 PM'})
            for dow, label in DOW_CHOICES
        ]
        response = client.post(reverse('add_schedule'), post_data, follow=True)

        # saving takes us back to the schedule list
        final_url = response.redirect_chain[-1][0]
        self.assertTrue(final_url.endswith(reverse('edit_hours')))

        # there are now two schedules on the list
        schedules = response.context['schedules']
        assert_true(schedules.count() == 2)

    def test_jonathan_has_implemented_javascript_test_for_schedule_suggestions(self):
        self.fail()


def test_time_display():
    data = (
        ((12,0), (0,0), '12am'),
        ((12,0), (0,30), '12:30am'),
        ((10,0), (12,0), '12pm'),
        ((10,0), (12,15), '12:15pm'),
        ((10,0), (17,15), '5:15pm'),
        ((10,0), (11,15), '11:15am'),
    )
    for start, stop, expected in data:
        yield check_time_display, start, stop, expected


def check_time_display(start, stop, expected):
    if not Site.objects.count():
        load_fixtures('tiger.fixtures')
    schedule = Schedule.objects.create(site=Site.objects.all()[0])
    timeslot = TimeSlot(schedule=schedule, start=time(*start), stop=time(*stop), dow=1)
    assert_equal(timeslot.pretty_stop, expected)


def test_within_timeslot_spanning_midnight():
    if not Site.objects.count():
        load_fixtures('tiger.fixtures')
    now = datetime.now() 
    schedule = Schedule.objects.create(site=Site.objects.all()[0])
    timeslot = TimeSlot(schedule=schedule, start=time(23,0), stop=time(1, 0), dow=now.weekday())
    # need to test both sides of date divide
    # before open
    timeslot.now = lambda: now.replace(hour=22)
    location = Location.objects.all()[0]
    assert_equal(timeslot.get_availability(location), None)
    # while open, before midnight
    timeslot.now = lambda: now.replace(hour=23, minute=30)
    assert_equal(timeslot.get_availability(location), TIME_OPEN)
    # while open, after midnight
    timeslot.now = lambda: now.replace(hour=0, minute=30) + timedelta(days=1)
    assert_equal(timeslot.get_availability(location), TIME_OPEN)
    # after close
    timeslot.now = lambda: now.replace(hour=2, minute=30) + timedelta(days=1)
    assert_equal(timeslot.get_availability(location), None)


def test_timeslot_form_validation():
    data = (
        ('12:00 AM', '12:00 PM', time(0, 0), time(12, 0)),
        ('12:00 PM', '12:00 AM', time(12, 0), time(0, 0)),
    )
    for start_str, stop_str, start_time, stop_time in data:
        yield check_timeslot_form_validation, start_str, stop_str, start_time, stop_time

def check_timeslot_form_validation(start_str, stop_str, start_time, stop_time):
    form = TimeSlotForm({'start': start_str, 'stop': stop_str})
    form.is_valid()
    assert_true(form.is_valid())
    timeslot = form.save(commit=False)
    assert_equal(timeslot.start, start_time)
    assert_equal(timeslot.stop, stop_time)
