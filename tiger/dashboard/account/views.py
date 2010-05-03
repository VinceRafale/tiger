from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic.simple import direct_to_template

from tiger.accounts.forms import ContactInfoForm, CreditCardForm
from tiger.dashboard.account.forms import CancellationForm
from tiger.utils.chargify import Chargify


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
        return HttpResponseRedirect(reverse('cancelled'))
    else:
        form = CancellationForm()
    return direct_to_template(request, template='dashboard/account/cancel.html',
        extra_context={'form': form})

def update_contact(request):
    if request.method == 'POST':
        form = ContactInfoForm(request.POST, instance=request.site.account)
        if form.is_valid():
            account = form.save()
            user = request.user
            for attr in ('first_name', 'last_name', 'email'):
                setattr(user, attr, cleaned_data.get(attr, ''))
            user.save()
            return HttpResponseRedirect(reverse('account_home'))
    else:
        form = ContactInfoForm(instance=request.site.account)
    return direct_to_template(request, template='dashboard/account/update_contact.html',
        extra_context={'form': form})

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
        form = CreditCardForm(instance=request.site.account)
    return direct_to_template(request, template='dashboard/account/update_cc.html',
        extra_context={'form': form})
