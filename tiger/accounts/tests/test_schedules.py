from time import sleep
from datetime import time, datetime

from django.core.management import call_command
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client

from djangosanetesting.noseplugins import TestServerThread
from nose.tools import *
from poseur.fixtures import load_fixtures
from selenium import selenium

from tiger.accounts.forms import TimeSlotForm
from tiger.accounts.models import Site, Schedule, TimeSlot
from tiger.accounts.tests.dtstub import set_datetime
from tiger.utils.hours import *
from tiger.core.models import Section, Item
from tiger.core.tests.test_orders import data_for_order_form


class DefaultScheduleTestCase(TestCase):
    schedule = True

    #def test_default_schedule(self):
        #s = Site.objects.order_by('-id')[0]

        ## new sites should have no hours in one schedule
        #assert_true(s.schedule_set.count() == 1)
        #schedule = s.schedule_set.all()[0]
        #assert_true(schedule.timeslot_set.count() == 0)

        ## default schedule should be associated with the default location
        ##assert_true(schedule == s.location_set.all()[0].schedule)



class AddEditScheduleTest(TestCase):
    schedule = True

    @classmethod
    def setup_class(cls):
        if not Site.objects.count():
            load_fixtures('tiger.fixtures')
        cls.server_thread = TestServerThread('127.0.0.1', 8000)
        cls.server_thread.start()
        cls.server_thread.started.wait()
        if cls.server_thread.error:
            raise cls.server_thread.error
        cls.sel = selenium(
            'localhost',
            4444,
            '*firefox',
            'http://foo.takeouttiger.com:8000' 
        )
        cls.sel.start()
        cls.sel.open('/dashboard/login/')
        cls.sel.type('email', 'test@test.com')
        cls.sel.type('password', 'password')
        cls.sel.click("css=input[type='submit']")
        cls.sel.wait_for_page_to_load(2000)

    @classmethod
    def teardown_class(cls):
        cls.sel.close()
        cls.server_thread.join()

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

    def test_schedule_suggestions(self):
        # we click edit to edit the new schedule
        schedule = Schedule.objects.all()[0]
        url = reverse('edit_schedule', args=[schedule.id])
        self.sel.open(url)
        # display is blank for starters
        self.assertEquals(self.sel.get_value('hours-display'), '')
        # changing the values of the times automatically updates suggestions for the display of the schedule
        # T-S, 9am-9pm
        for i in range(1, 6):
            self.sel.type('id_%d-start' % i, '09:00 AM')
            self.sel.type('id_%d-stop' % i, '09:00 PM')
        self.sel.fire_event('id_5-stop', 'blur')
        sleep(2)
        self.assertEquals(self.sel.get_value('hours-display'), 'Tue-Sat 9am-9pm')


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
    assert_equal(timeslot.get_availability(), None)
    # while open, before midnight
    timeslot.now = lambda: now.replace(hour=23, minute=30)
    assert_equal(timeslot.get_availability(), TIME_OPEN)
    # while open, after midnight
    timeslot.now = lambda: now.replace(hour=0, minute=30) + timedelta(days=1)
    assert_equal(timeslot.get_availability(), TIME_OPEN)
    # after close
    timeslot.now = lambda: now.replace(hour=2, minute=30) + timedelta(days=1)
    assert_equal(timeslot.get_availability(), None)


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
