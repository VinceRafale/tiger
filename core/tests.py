from django.test import TestCase

class CartMiddlewareTestCase(TestCase):
    def test_request_has_cart(self):
        """Tests that the ``ShoppingCartMiddleware`` successfully set the ``cart``
        attribute on the ``HttpRequest`` object.
        """
        self.fail()

    def test_cart_add(self):
        """Tests that the ``add`` method of the shopping cart works correctly.
        """
        self.fail()

    def test_cart_remove(self):
        """Tests that the ``remove`` method of the shopping cart works correctly.
        """
        self.fail()

    def test_cart_clear(self):
        """Tests that the ``clear`` method of the shopping cart works correctly.
        """
        self.fail()

    def test_cart_persists_between_requests(self):
        """Tests that the user's shopping cart contents are correctly retrieved
        when the cart is edited and a new HTTP request is made.
        """
        self.fail()

    def test_cart_persists_after_login(self):
        """Tests that the user's shopping cart contents are not lost when moving
        from an unauthenticated to an authenticated session.
        """
        self.fail()

