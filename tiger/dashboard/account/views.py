from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic.simple import direct_to_template

from tiger.accounts.forms import CreditCardForm
from tiger.dashboard.account.forms import CancellationForm
from tiger.utils.chargify import Chargify


@login_required
def cancel(request):
    if request.method == 'POST':
        form = CancellationForm(request.POST)
        form.full_clean()
        subscription_id = request.site.account.subscription_id
        chargify = Chargify(settings.CHARGIFY_API_KEY, settings.CHARGIFY_SUBDOMAIN)
        subscription = chargify.subscriptions.delete(subscription_id=subscription_id, data={
            'subscription': {
                'cancellation_message': form.cleaned_data.get('comments', '') 
            }
        })
        request.user.delete()
        #TODO: finish cancelled template
        return HttpResponseRedirect('http://www.takeouttiger.com' + reverse('cancelled', urlconf='tiger.tiger_urls'))
    else:
        form = CancellationForm()
    return direct_to_template(request, template='dashboard/account/cancel.html',
        extra_context={'form': form})

@login_required
def update_cc(request):
    if request.method == 'POST':
        form = CreditCardForm(request.POST, instance=request.site.account)
        if form.is_valid():
            account = form.save(commit=False)
            account.card_number = form.subscription['credit_card']['masked_card_number']
            account.card_type = form.subscription['credit_card']['card_type']
            account.save()
            return HttpResponseRedirect(reverse('update_cc'))
    else:
        instance = request.site.account
        form = CreditCardForm(instance=instance)
    return direct_to_template(request, template='dashboard/account/update_cc.html',
        extra_context={'form': form})
