from django.test import TransactionTestCase as BaseTestCase
from django.db import transaction

from django.core.management import call_command
from poseur.fixtures import load_fixtures


class TestCase(BaseTestCase):
    def _fixture_setup(self):
        super(TestCase, self)._fixture_setup()
        if hasattr(self, 'poseur_fixtures'):
            try:
                load_fixtures(self.poseur_fixtures)
            except IntegrityError:
                transaction.rollback()
