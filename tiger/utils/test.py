from django.conf import settings
from django.core.management import call_command
from django.test import TestCase as BaseTestCase
from django.utils.importlib import import_module

from poseur.fixtures import load_fixtures


class TestCase(BaseTestCase):
    @classmethod
    def setup_class(cls):
        if hasattr(cls, 'poseur_fixtures'):
            call_command('flush', verbosity=0, interactive=False, database='default')
            load_fixtures(cls.poseur_fixtures)

    def _pre_setup(self):
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
