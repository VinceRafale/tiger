from lxml.html import fromstring

from django.test import TestCase
from django.test.client import Client


class DomainDetectionMiddlewareTestCase(TestCase):
    fixtures = ['test_site_data.json']

    def test_takeouttiger_com(self):
        """Tests that requests to www.takeouttiger.com trigger the correct
        URLconf.
        """
        client = Client(HTTP_HOST='www.takeouttiger.com')
        response = client.get('/')
        doc = fromstring(response.content)
        self.assertTrue('Takeout Tiger' in doc.xpath('//title')[0].text)

    def test_subdomain_request(self):
        """Tests that requests to <foo>.takeouttiger.com server the correct
        pages for site <foo>.
        """
        for name in ('Foo', 'Bar'):
            client = Client(HTTP_HOST='%s.takeouttiger.com' % name.lower())
            response = client.get('/')
            doc = fromstring(response.content)
            self.assertTrue(name in doc.xpath('//title')[0].text)

    def test_domain_request(self):
        """Tests that requests to www.<foo>.com server the correct pages for 
        site <foo>.
        """
        for name in ('Foo', 'Bar'):
            client = Client(HTTP_HOST='www.%s.com' % name.lower())
            response = client.get('/')
            doc = fromstring(response.content)
            self.assertTrue(name in doc.xpath('//title')[0].text)


class NotificationSettingsTestCase(TestCase):
    def test_add_cron(self):
        """Tests that a new cron job is added to the crontab when notification 
        settings are saved for the first time.
        """
        self.fail()

    def test_edit_cron(self):
        """Tests that an existing cron job is edited rather than created anew 
        when notification settings are changed.
        """
        self.fail()

    def test_remove_cron(self):
        """Tests that a cron job is removed when notification settings are 
        removed.
        """
        self.fail()

    def test_remove_cron_on_delete(self):
        """Tests that a notification settings object properly cleans up after 
        itself when deleted.
        """
        self.fail()
