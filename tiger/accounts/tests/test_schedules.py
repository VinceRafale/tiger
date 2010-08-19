from time import sleep
from datetime import time, datetime

from django.core.management import call_command
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client

from nose.tools import *
from poseur.fixtures import load_fixtures
from selenium import selenium
from djangosanetesting.noseplugins import TestServerThread
from lxml.html import parse

from tiger.accounts.models import Site, Schedule, TimeSlot
from tiger.accounts.tests.dtstub import set_datetime
from tiger.utils.hours import DOW_CHOICES 
from tiger.core.models import Section, Item
from tiger.core.tests.test_orders import data_for_order_form


class ScheduleRestrictionTestCase(TestCase):
    schedule = True

    @classmethod
    def setup_class(cls):
        if not Site.objects.count():
            load_fixtures('tiger.fixtures')

    @classmethod
    def teardown_class(cls):
        call_command('flush', verbosity=0, interactive=False)

    def test_default_schedule(self):
        s = Site.objects.all()[0]

        # new sites should have no hours in one schedule
        assert_true(s.schedule_set.count() == 1)
        schedule = s.schedule_set.all()[0]
        assert_true(schedule.timeslot_set.count() == 0)

        # default schedule should be associated with the default location
        #assert_true(schedule == s.location_set.all()[0].schedule)


class ScheduleRestrictionTestCase(TestCase):
    schedule = True

    @classmethod
    def setup_class(cls):
        if not Site.objects.count():
            load_fixtures('tiger.fixtures')
        schedule = Schedule.objects.all()[0]
        for dow, label in DOW_CHOICES:
            TimeSlot.objects.create(dow=dow, schedule=schedule, start=time(9, 0), stop=time(9 + 12, 0))

    @classmethod
    def teardown_class(cls):
        call_command('flush', verbosity=0, interactive=False)

    def setUp(self):
        self.client = Client(HTTP_HOST='foo.takeouttiger.com')

    def test_orders_against_location_schedule(self):
        # test application to location / online ordering restrictions
        set_datetime(datetime(2010, 8, 18, 12, 30))
        print self.client.get('/').content
        item = Item.objects.order_by('?')[0]
        response = self.client.post(reverse('order_item', kwargs={'section': item.section.slug, 'item': item.slug}), data_for_order_form(item), follow=True)
        print response.redirect_chain
        self.assertContains(response, 'added to your order. You can')

        set_datetime(datetime(2010, 8, 18, 22, 30))
        item = Item.objects.order_by('?')[0]
        response = self.client.post(reverse('order_item', kwargs={'section': item.section.slug, 'item': item.slug}), data_for_order_form(item), follow=True)
        self.assertContains(response, 'is currently closed')

    def test_orders_against_section_schedule(self):
        # test application to sections / online ordering restrictions
        self.fail()

    def test_orders_against_price_point_schedule(self):
        # test application to price point / online ordering restrictions
        self.fail()


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

