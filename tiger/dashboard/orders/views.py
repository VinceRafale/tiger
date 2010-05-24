from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic.simple import direct_to_template

from tiger.core.forms import OrderSettingsForm, OrderPaymentForm, GeocodeError
from tiger.core.models import Order

def home(request):
    return direct_to_template(request, template='dashboard/orders/order_history.html', extra_context={
        'orders': Order.objects.order_by('-timestamp')[:10] 
    })

def order_detail(request, order_id):
    return direct_to_template(request, template='dashboard/orders/order_detail.html', extra_context={
        'order': Order.objects.get(id=order_id) 
    })

def order_options(request):
    if request.method == 'POST':
        form = OrderSettingsForm(request.POST, site=request.site, instance=request.site.ordersettings)
        if form.is_valid():
            form.save()
            site = request.site
            site.email = form.cleaned_data.get('email', '')
            site.fax = form.cleaned_data.get('fax', '')
            site.save()
            messages.success(request, 'Your order options have been updated.')
            return HttpResponseRedirect(reverse('dashboard_orders'))
        #TODO: olwidget doesn't handle malformed data very nicely.  This is a
        # hackish workaround for the time being.
        if 'delivery_area' in form._errors:
            form = OrderSettingsForm(site=request.site, instance=request.site.ordersettings)
            messages.error(request, 'Some of your shape data was corrupted. Please redraw your area.')
    else:
        try:
            form = OrderSettingsForm(site=request.site, instance=request.site.ordersettings)
        except GeocodeError:
            messages.error(request, "Please be sure you have a valid street address, city, state and zip.  We can't calculate your position on the map without it.")
            return HttpResponseRedirect(reverse('dashboard_location'))
    return direct_to_template(request, template='dashboard/orders/order_options.html', extra_context={
        'form': form
    })

def order_payment(request):
    if request.method == 'POST':
        form = OrderPaymentForm(request.POST, instance=request.site.ordersettings)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your settings have been updated.')
            return HttpResponseRedirect(reverse('dashboard_orders'))
    else:
        form = OrderPaymentForm(instance=request.site.ordersettings)
    return direct_to_template(request, template='dashboard/orders/order_payment.html', extra_context={
        'form': form
    })
