from unittest import TestCase
import time
from nose.tools import *
from selenium import selenium
from poseur.fixtures import load_fixtures

from django.core.urlresolvers import reverse

from tiger.accounts.models import Site, Schedule
from tiger.utils.hours import DOW_CHOICES 


class AddEditScheduleTest(TestCase):
    selenium_test = True

    def setUp(self):
        self.selenium.open('/dashboard/')
        self.selenium.type('id_email', 'test@test.com')
        self.selenium.type('id_password', 'password')
        self.selenium.click('css=input[type="submit"]')

    # edit schedule
    def test_schedule_dashboard(self):
        self.selenium.click('link=Hours')
        # schedule list should have one schedule for starters
        self.selenium.assertElementNotPresent('tbody tr:nth-child(2)')
        
        # we click "new" to go to the new schedule form and add a new schedule
        response = c.get(reverse('add_schedule'))
        post_data = reduce(lambda x, y: x.update(y), [
            {'%d-start': '09:00 AM',  '%d-stop': '09:00 PM'}
            for dow, label in DOW_CHOICES
        ])
        response = c.post(reverse('add_schedule'), post_data, follow=True)

        # saving takes us back to the schedule list
        assert_true(request.path, reverse('edit_hours'))

        # there are now two schedules on the list
        schedules = response.context['schedules']
        assert_true(schedules.count() == 2)

    def test_schedule_suggestions(self):
        # we click edit to edit the new schedule
        url = reverse('edit_schedule', args=[schedule.id])
        self.selenium.open(url)
        # and the values in the schedule form match what's in the database
        for timeslot in schedule.timeslot_set.all():
            start_name = '%d-start' % timeslot.id
            stop_name = '%d-stop' % timeslot.id
            assert False
        # changing the values of the times automatically updates suggestions for the display of the schedule
        assert False

