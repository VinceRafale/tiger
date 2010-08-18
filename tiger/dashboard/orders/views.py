from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import render_to_string
from django.views.generic.simple import direct_to_template

from tiger.core.forms import OrderSettingsForm, OrderPaymentForm, GeocodeError, OrderMessageForm
from tiger.core.models import Order

@login_required
def home(request):
    return direct_to_template(request, template='dashboard/orders/order_history.html', extra_context={
        'orders': Order.objects.filter(site=request.site).order_by('-timestamp')[:10] 
    })

@login_required
def get_new_orders(request):
    new_orders = Order.objects.filter(site=request.site).order_by('-timestamp')
    rows = render_to_string('dashboard/orders/new_order.html', {'orders': new_orders})
    return HttpResponse(rows)


@login_required
def order_detail(request, order_id):
    order = Order.objects.get(id=order_id) 
    order.unread = False
    order.save()
    return direct_to_template(request, template='dashboard/orders/order_detail.html', extra_context={
        'order': order,
        'cart': order.get_cart()
    })

@login_required
def order_options(request):
    if request.method == 'POST':
        form = OrderSettingsForm(request.POST, site=request.site, instance=request.site.ordersettings)
        if form.is_valid():
            form.save()
            site = request.site
            site.email = form.cleaned_data.get('email', '')
            site.fax_number = form.cleaned_data.get('fax', '')
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

@login_required
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

@login_required
def order_messages(request):
    if request.method == 'POST':
        form = OrderMessageForm(request.POST, instance=request.site.ordersettings)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your ordering messages have been updated.')
            return HttpResponseRedirect(reverse('dashboard_orders'))
    else:
        form = OrderMessageForm(instance=request.site.ordersettings)
    return direct_to_template(request, template='dashboard/orders/order_messages.html', extra_context={
        'form': form
    })
