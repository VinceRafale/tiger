from nose.tools import *
from nose.exc import SkipTest

from should_dsl import should, should_not

from tiger.core.models import LocationStockInfo, Order
from tiger.accounts.models import Site, Location
from tiger.fixtures import FakeOrder
from tiger.sales.models import Account, Plan
from tiger.utils.test import TestCase


class DashboardControlsTestCase(TestCase):
    fixtures = ['plans.json']
    poseur_fixtures = 'tiger.fixtures'

    def setUp(self):
        self.site = Site.objects.all()[0]
        second_location = Location.objects.create(site=self.site, schedule=self.site.schedule_set.all()[0])
        self.client.login(email='test@test.com', password='password', site=self.site)

    def test_one_location_has_no_selector(self):
        self.site.location_set.all()[0].delete()
        response = self.client.get('/dashboard/menu/', follow=True)
        response.css("#change-location") |should| have(0).elements

    def test_two_locations_has_selector(self):
        response = self.client.get('/dashboard/menu/')
        response.css("#change-location") |should| have(1).element

    def test_selector_changes_location_in_context(self):
        response = self.client.get('/dashboard/menu/')
        initial_location = response.context['location']
        response = self.client.post('/dashboard/change-location/', {
            'loc': Location.objects.exclude(id=initial_location.id)[0].id}, follow=True)
        new_location = response.context['location']
        initial_location |should_not| equal_to(new_location)

    def test_changing_location_changes_stock_levels(self):
        menu_item = self.site.item_set.all()[0]
        checkbox = "input[name='out_of_stock-%s']" % menu_item.id

        stock1, stock2 = menu_item.locationstockinfo_set.all()
        stock1.out_of_stock = True
        stock1.save()
        stock2.out_of_stock = False
        stock2.save()

        self.client.post('/dashboard/change-location/', {
            'loc': stock1.location.id}, follow=True)
        response = self.client.get('/dashboard/menu/')
        response.css(checkbox)[0] |should| be_checked
        
        self.client.post('/dashboard/change-location/', {
            'loc': stock2.location.id}, follow=True)
        response = self.client.get('/dashboard/menu/')
        response.css(checkbox)[0] |should_not| be_checked

    def test_changing_location_changes_orders_list(self):
        self.site.plan = Plan.objects.get(has_online_ordering=True)
        self.site.save()
        loc1, loc2 = self.site.location_set.all()
        FakeOrder.generate(2)
        order1, order2 = Order.objects.all()
        order1.location = loc1
        order1.save()
        order2.location = loc2
        order2.save()

        self.client.post('/dashboard/change-location/', {'loc': loc1.id})
        response = self.client.get('/dashboard/orders/')
        response.css("#%d" % order1.id) |should| have(1).element
        response.css("#%d" % order2.id) |should| have(0).elements
        
        self.client.post('/dashboard/change-location/', {'loc': loc2.id})
        response = self.client.get('/dashboard/orders/')
        response.css("#%d" % order2.id) |should| have(1).element
        response.css("#%d" % order1.id) |should| have(0).elements


