
my_house = (42.213633, -72.567852)
moms_house = (41.876919, -72.631275)

#multiple addresses appear in sidebar and footer
#pdf menu location list...

def test_delivery_area():
    location = Site.location_set.all()[0]
    # delivery area encompasses western mass
    assert_true(location.contains(my_house))
    assert_false(location.contains(moms_house))

@with_setup(setup, teardown)
def test_dashboard_location_selector():
    # test no selector w/ one location
    #TODO: get client
    response = client.get(reverse("dashboard_menu"))
    body = lxml(response.content)
    assert_false(len(body.cssselect("a#change-location")))
    # test selector w/ 2 locations
    site = Site.objects.all()[0]
    location = Location.objects.create(site=site)
    response = client.get(reverse("dashboard_menu"))
    body = lxml(response.content)
    assert_true(len(body.cssselect("a#change-location")))
    # post to switch URL
    response = client.post(reverse("dashboard_change_location"), {"location_id": location.id}, follow=True)
    # assert page contains selected location
    assert_true("Location: %s" % location.display in response.content)

def test_per_location_out_of_stock():
    # set location
    # post to update out of stock for an item
    # refresh page
    # one location has an item in stock
    # one without 
    assert False

def test_per_location_orders_list():
    # create some orders for both locations
    # set location
    # assert orders for location
    # change location
    # assert orders for location
    assert False

def test_location_on_order_detail():
    # assert page contains location display value
    assert False

def test_per_location_sales_tax():
    # set sales tax per location
    # place orders for each location
    # test that sales tax matches
    assert False

def test_per_location_order_delivery():
    # set different e-mail addresses for receipt of orders
    # place order to one location
    # check e-mail outbox for matching address
    # place order to other location
    # check e-mail outbox for matching address
    assert False

def test_customer_location_selector():
    # test no selector w/ one location
    # test selector w/ 2 locations
    # post to switch URL
    # assert redirects
    # assert page contains selected location
    assert False

def test_no_items_allowed_without_location():
    assert False

def test_delivery_option_for_blank_delivery_area():
    assert False

def test_items_create_stock_records_for_locations():
    assert False

def test_locations_create_stock_records_for_items():
    assert False
