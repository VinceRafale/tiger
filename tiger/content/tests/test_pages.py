import os
import shutil

from lxml.html import document_fromstring
from nose.tools import assert_equal
from nose.exc import SkipTest

from django.conf import settings
from django.core.files.base import ContentFile

from tiger.content.models import Content, MenuItem
from tiger.accounts.models import Site
from tiger.utils.test import TestCase


class ContentOrderingTestCase(TestCase):
    poseur_fixtures = 'tiger.fixtures'

    def setUp(self):
        self.site = Site.objects.all()[0]
        self.homepage = Content.objects.get(site=self.site, slug='homepage')
        self.find_us = Content.objects.get(site=self.site, slug='find-us')

    def test_default_homepage_position(self):
        """The default homepage position should be 1
        """
        menu_item = MenuItem.objects.get(page__slug='homepage')
        assert_equal(1, menu_item.position)

    def test_homepage_link_position(self):
        """The default homepage link should appear first in the menu
        """
        response = self.client.get('/', follow=True, SERVER_NAME='foo.takeouttiger.com')
        doc = document_fromstring(response.content)
        print response.content
        assert_equal('Home', doc.cssselect('#menu li a')[0].text)

    def test_homepage_title_change(self):
        """Changing the default homepage title should not alter its position in
        the menu
        """
        menu_item = MenuItem.objects.get(page__slug='homepage')
        menu_item.title = 'Changed'
        menu_item.save()
        response = self.client.get('/', follow=True, SERVER_NAME='foo.takeouttiger.com')
        doc = document_fromstring(response.content)
        assert_equal('Changed', doc.cssselect('#menu li a')[0].text)

    def test_move_find_us(self):
        """Moving the "Find Us" page to the first position should change its
        position in the menu
        """
        menu_item = MenuItem.objects.get(page__slug='homepage')
        map_item = MenuItem.objects.get(page__slug='find-us')
        menu_item.position = 4
        menu_item.save()
        map_item.position = 1
        map_item.save()
        response = self.client.get('/', follow=True, SERVER_NAME='foo.takeouttiger.com')
        doc = document_fromstring(response.content)
        assert_equal('Find us', doc.cssselect('#menu li a')[0].text)

    def test_move_root(self):
        """Moving the "Find Us" page to the first position should change the
        root URL to be the "Find Us" page
        """
        menu_item = MenuItem.objects.get(page__slug='homepage')
        map_item = MenuItem.objects.get(page__slug='find-us')
        menu_item.position = 4
        menu_item.save()
        map_item.position = 1
        map_item.save()
        response = self.client.get('/', follow=True, SERVER_NAME='foo.takeouttiger.com')
        doc = document_fromstring(response.content)
        assert_equal('Find us', doc.cssselect('h1')[0].text)


class ContentAbsoluteUrlTestCase(TestCase):
    poseur_fixtures = 'tiger.fixtures'

    def setUp(self):
        self.site = Site.objects.all()[0]

    def tearDown(self):
        try:
            shutil.rmtree(os.path.join(settings.MEDIA_ROOT, 'uploads'))
        except:
            pass

    def test_menu_link(self):
        """get_absolute_url of "Menu" links always returns "/menu/"
        """
        item = MenuItem.objects.create(site=self.site, link_type=MenuItem.MENU)
        assert_equal('/menu/', item.get_absolute_url())

    def test_page_link(self):
        """get_absolute_url of "Page" links always returns
        "/pages/<id>/<slug>/"
        """
        item = MenuItem.objects.create(site=self.site, link_type=MenuItem.PAGE, page=Content.objects.get(slug='find-us'))
        assert_equal('/pages/2/find-us/', item.get_absolute_url())

    def test_link_link(self):
        """get_absolute_url of "Link" links always returns content.url
        """
        item = MenuItem.objects.create(site=self.site, link_type=MenuItem.URL, url='http://google.com')
        assert_equal('http://google.com', item.get_absolute_url())

    def test_file_link(self):
        """get_absolute_url of "File" links always returns content.upload.url
        """
        item = MenuItem.objects.create(site=self.site, link_type=MenuItem.UPLOAD)
        item.upload.save('foo.sh', ContentFile('#!/bin/bash'))
        assert_equal('/static/' + item.upload.name, item.get_absolute_url())

