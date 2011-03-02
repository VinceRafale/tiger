from datetime import date

from django.conf import settings
from django.core.management.base import NoArgsCommand

from tiger.sales.models import Account


class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        for s in Account.objects.all():
            invoice = s.create_invoice()

