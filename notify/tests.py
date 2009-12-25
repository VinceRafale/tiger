from django.test import TestCase


class SendFaxTestCase(TestCase):
    def test_send_page(self):
        """Tests that the Interfax API client successfully sends a fax
        and returns the appropriate ``Fax`` model instance.
        """
        self.fail()
