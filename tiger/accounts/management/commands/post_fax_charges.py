from datetime import date

from django.conf import settings
from django.core.management.base import NoArgsCommand

from tiger.accounts.models import Site
from tiger.utils.chargify import Chargify, ChargifyError


class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        chargify = Chargify(settings.CHARGIFY_API_KEY, settings.CHARGIFY_SUBDOMAIN)
        for s in Site.objects.all():
            if s.account.subscription_id:
                unlogged_faxes = s.fax_set.filter(logged=False)
                page_count = sum(fax.page_count or 0 for fax in unlogged_faxes)
                if page_count:
                    response = chargify.subscriptions.components.usages.create(
                        subscription_id=s.account.subscription_id,
                        component_id=224,
                        data=dict(usage={
		    	    'quantity': page_count,
		    	    'memo': 'Fax charges for %s' % date.today().strftime('%x')
                }))
                unlogged_faxes.update(logged=True)

                unlogged_texts = s.sms.sms_set.filter(logged=False)
                count = unlogged_texts.count()
                if count:
                    response = chargify.subscriptions.components.usages.create(
                        subscription_id=s.account.subscription_id,
                        component_id=2888,
                        data=dict(usage={
		    	    'quantity': count,
		    	    'memo': 'SMS charges for %s' % date.today().strftime('%x')
                }))
                unlogged_texts.update(logged=True)
