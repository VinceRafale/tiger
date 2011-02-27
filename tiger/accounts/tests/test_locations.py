from nose.tools import *
from nose.exc import SkipTest
from urlparse import urlsplit

from django.core.urlresolvers import reverse

from should_dsl import should, should_not, matcher

from tiger.core.models import LocationStockInfo, Order, Item, Variant
from tiger.core.tests.test_order_availability import data_for_order_form, setup_timeslots
from tiger.accounts.models import Site, Location
from tiger.fixtures import FakeOrder
from tiger.sales.models import Account, Plan
from tiger.utils.test import TestCase


@matcher
def redirect_to():
    def test_redirects_to(response, url):
        scheme, netloc, path, query, fragment = urlsplit(response['Location'])
        return path == url
    return test_redirects_to, "%s did %s redirect to %s."


class LocationTestCase(TestCase):
    fixtures = ['plans.json']
    poseur_fixtures = 'tiger.fixtures'

    @classmethod
    def setup_class(cls):
        super(LocationTestCase, cls).setup_class()
        setup_timeslots(0)()
        site = Site.objects.all()[0]
        schedule = site.schedule_set.all()[0]
        Location.objects.create(site=site, schedule=schedule)
        for location in Location.objects.all():
            location.schedule = schedule
            location.save()

    def _pre_setup(self):
        super(LocationTestCase, self)._pre_setup()
        self.site = Site.objects.all()[0]
        self.site.plan = Plan.objects.filter(has_online_ordering=True)[0]
        self.site.save()


class LocationControlsTestCase(LocationTestCase):
    def setUp(self):
        self.site = Site.objects.all()[0]
        self.client.login(email='test@test.com', password='password', site=self.site)

    def test_one_location_has_no_dashboard_selector(self):
        self.site.location_set.all()[0].delete()
        response = self.client.get('/dashboard/menu/', follow=True)
        response.css("#change-location") |should| have(0).elements

    def test_two_locations_has_dashboard_selector(self):
        response = self.client.get('/dashboard/menu/')
        response.css("#change-location") |should| have(1).element

    def test_selector_changes_location_in_dashboard_context(self):
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

    def test_one_location_has_no_homepage_selector(self):
        self.site.location_set.all()[0].delete()
        response = self.client.get('/', follow=True)
        response.css("#change-location") |should| have(0).elements

    def test_one_location_has_no_change_location_page(self):
        self.site.location_set.all()[0].delete()
        response = self.client.get('/change-location/')
        response.status_code |should| equal_to(404)

    def test_two_locations_has_homepage_selector(self):
        response = self.client.get('/')
        response.css("#change-location") |should| have(1).element

    def test_homepage_has_no_initial_location(self):
        response = self.client.get('/')
        response.context['location'] |should| be(None)

    def test_selector_sets_location_in_homepage_context(self):
        response = self.client.post('/change-location/', {
            'loc': 2}, follow=True)
        new_location = response.context['location']
        new_location.id |should| equal_to(2)

    def test_no_items_allowed_without_location(self):
        response = self.client.post('/change-location/', {
            'loc': 2}, follow=True)
        response = self.add_to_cart()
        response |should_not| redirect_to('/change-location/')

    def test_items_allowed_with_location(self):
        response = self.add_to_cart()
        response |should| redirect_to('/change-location/')

    def test_changing_location_clears_cart(self):
        self.client.post('/change-location/', {
            'loc': 2}, follow=True)
        response = self.add_to_cart()
        response = self.client.get('/')
        response.css("p.has-items") |should| have(1).element
        response = self.client.post('/change-location/', {
            'loc': 1}, follow=True)
        response = self.client.get('/')
        response.css("p.has-items") |should| have(0).elements

    def add_to_cart(self):
        item = Variant.objects.all()[0].item
        item.archived = item.out_of_stock = False
        item.save()
        order_url = reverse('order_item', kwargs={'section_id': item.section.id, 'section_slug': item.section.slug, 'item_id': item.id, 'item_slug': item.slug})
        data = data_for_order_form(item)
        return self.client.post(order_url, data)


class DataPopulationTestCase(LocationTestCase):
    def setUp(self):
        self.site = Site.objects.all()[0]

    def test_items_create_stock_records_for_locations(self):
        item = Item.objects.create(
            section=self.site.section_set.all()[0],
            site=self.site,
            name='foo',
            description=''
        )
        for location in Location.objects.all():
            stock_level = LocationStockInfo.objects.get(location=location, item=item)
            stock_level |should_not| be_out_of_stock

    def test_locations_create_stock_records_for_items(self):
        location = Location.objects.create(site=self.site, schedule=self.site.schedule_set.all()[0])
        for item in Item.objects.all():
            stock_level = LocationStockInfo.objects.get(location=location, item=item)
            stock_level |should_not| be_out_of_stock


class OrderFormTestCase(LocationTestCase):
    def setUp(self):
        self.site = Site.objects.all()[0]

    def test_location_on_order_detail(self):
        # assert page contains location display value
        raise SkipTest()

    def test_per_location_sales_tax(self):
        # set sales tax per location
        # place orders for each location
        # test that sales tax matches
        raise SkipTest()

    def test_per_location_order_delivery(self):
        # set different e-mail addresses for receipt of orders
        # place order to one location
        # check e-mail outbox for matching address
        # place order to other location
        # check e-mail outbox for matching address
        raise SkipTest()

    def test_delivery_option_for_blank_delivery_area(self):
        raise SkipTest()
