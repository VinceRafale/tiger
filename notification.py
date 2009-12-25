import sys

from django.core.management import setup_environ
import settings
setup_environ(settings)

from tiger.accounts.models import Site
from tiger.core.models import Item
from tiger.notify.tasks import SendFaxTask


def run(site_id):
    site = Site.objects.get(id=site_id)
    html = Item.objects.render_specials_to_string(site)
    SendFaxTask.delay(site, site.subscribers, html)


if __name__ == '__main__':
    run(sys.argv[1])
