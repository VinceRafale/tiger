import types
from django.conf import settings
from django.test.client import ClientHandler, Client
from django.core.management import call_command
from django.test import TestCase as BaseTestCase
from django.utils.importlib import import_module

from lxml.html import fromstring

from poseur.fixtures import load_fixtures

def css(self, selector):
    body = fromstring(self.content)
    return body.cssselect(selector)


class TigerClientHandler(ClientHandler):
    def __call__(self, environ):
        response = super(TigerClientHandler, self).__call__(environ)
        setattr(response, 'css', types.MethodType(css, response))
        return response


class TigerClient(Client):
    def __init__(self, enforce_csrf_checks=False, **defaults):
        super(TigerClient, self).__init__(**defaults)
        self.handler = TigerClientHandler(enforce_csrf_checks)


class TestCase(BaseTestCase):
    @classmethod
    def setup_class(cls):
        if hasattr(cls, 'poseur_fixtures'):
            call_command('flush', verbosity=0, interactive=False, database='default')
            load_fixtures(cls.poseur_fixtures)

    def _pre_setup(self):
        self.client = TigerClient(HTTP_HOST='foo.takeouttiger.com')
        super(TestCase, self)._pre_setup()
        if hasattr(self, 'patch_settings'):
            for settings_module, patchables in self.patch_settings.items():
                mod = import_module(settings_module)
                for patchable in patchables:
                    setattr(self, patchable, getattr(settings, patchable))
                    setattr(settings, patchable, getattr(mod, patchable))

    def _post_teardown(self):
        super(TestCase, self)._post_teardown()
        if hasattr(self, 'patch_settings'):
            for settings_module, patchables in self.patch_settings.items():
                for patchable in patchables:
                    setattr(settings, patchable, getattr(self, patchable))

