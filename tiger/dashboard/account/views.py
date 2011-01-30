from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.views.generic.simple import direct_to_template

from tiger.accounts.forms import CreditCardForm, BasicInfoForm
from tiger.accounts.models import Site
from tiger.dashboard.account.forms import CancellationForm
from tiger.sales.models import Account
from tiger.utils.chargify import Chargify
from tiger.utils.views import add_edit_site_object


@login_required
def cancel(request):
    if request.site.managed:
        raise Http404
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
        request.site.location_set.all().delete()
        request.user.delete()
        return HttpResponseRedirect('http://www.takeouttiger.com')
    else:
        form = CancellationForm()
    return direct_to_template(request, template='dashboard/account/cancel.html',
        extra_context={'form': form})

@login_required
def basic_info(request):
    if request.method == 'POST':
        form = BasicInfoForm(request.POST, instance=request.site)
        if form.is_valid():
            form.save()
            messages.success(request, 'Info updated successfully.')
            return HttpResponseRedirect(reverse('dashboard_menu'))
    else:
        form = BasicInfoForm(instance=request.site)
    return direct_to_template(request, template='dashboard/account/basic_info.html',
        extra_context={'form': form})

@login_required
def billing_history(request):
    if request.site.managed:
        raise Http404
    return direct_to_template(request, template='dashboard/account/billing_history.html')

@login_required
def update_cc(request):
    if request.site.managed:
        raise Http404
    if request.method == 'POST':
        form = CreditCardForm(request.POST, instance=request.site.account)
        if form.is_valid():
            account = form.save(commit=False)
            account.card_number = form.subscription['credit_card']['masked_card_number']
            account.card_type = form.subscription['credit_card']['card_type']
            account.subscription_id = form.subscription['id']
            account.customer_id = form.subscription['customer']['id']
            account.status = Account.STATUS_ACTIVE
            account.save()
            return HttpResponseRedirect(reverse('update_cc'))
    else:
        instance = request.site.account
        form = CreditCardForm(instance=instance)
    return direct_to_template(request, template='dashboard/account/update_cc.html',
        extra_context={'form': form})
