from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template.loader import render_to_string
from django.views.generic.simple import direct_to_template

from tiger.accounts.forms import OrderSettingsForm
from tiger.core.forms import OrderPaymentForm, GeocodeError, OrderMessageForm
from tiger.core.models import Order


def online_ordering_required(func):
    def wrapped(request, *args, **kwargs):
        if not request.site.plan.has_online_ordering:
            raise Http404
        return func(request, *args, **kwargs)
    return wrapped


@login_required
@online_ordering_required
def home(request):
    return direct_to_template(request, template='dashboard/orders/order_history.html', extra_context={
        'orders': request.location.order_set.all()
    })

@login_required
@online_ordering_required
def get_new_orders(request):
    new_orders = Order.objects.filter(site=request.site).order_by('-timestamp')[:10]
    rows = render_to_string('dashboard/orders/new_order.html', {'orders': new_orders})
    return HttpResponse(rows)


@login_required
@online_ordering_required
def order_detail(request, order_id):
    order = Order.objects.get(id=order_id) 
    if order.unread:
        order.unread = False
        order.save()
    return direct_to_template(request, template='dashboard/orders/order_detail.html', extra_context={
        'order': order,
        'cart': order.get_cart()
    })

@login_required
@online_ordering_required
def order_pdf(request, order_id):
    order = Order.objects.get(id=order_id) 
    response = HttpResponse(order.get_pdf_invoice(), mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=invoice.pdf'
    return response

@login_required
@online_ordering_required
def order_options(request):
    location = request.location
    if request.method == 'POST':
        form = OrderSettingsForm(request.POST, site=request.site, instance=location)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your order options have been updated.')
            return HttpResponseRedirect(reverse('dashboard_orders'))
        #TODO: olwidget doesn't handle malformed data very nicely.  This is a
        # hackish workaround for the time being.
        if 'delivery_area' in form._errors:
            form = OrderSettingsForm(site=request.site, instance=location)
            messages.error(request, 'Some of your shape data was corrupted. Please redraw your area.')
    else:
        try:
            form = OrderSettingsForm(site=request.site, instance=location)
        except GeocodeError:
            messages.error(request, "Please be sure you have a valid street address, city, state and zip.  We can't calculate your position on the map without it.")
            return HttpResponseRedirect(reverse('dashboard_location'))
    return direct_to_template(request, template='dashboard/orders/order_options.html', extra_context={
        'form': form
    })

@login_required
@online_ordering_required
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
@online_ordering_required
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

@login_required
@online_ordering_required
def toggle_order_status(request):
    site = request.site
    location = request.location
    if location.enable_orders:
        location.enable_orders = False
    else:
        if not location.can_receive_orders():
            messages.error(request, "You must enter a fax number or e-mail address to receive online orders.") 
            return HttpResponseRedirect(reverse('order_options'))
        if not location.tax_rate:
            messages.error(request, "You must enter a sales tax rate to receive online orders.") 
            return HttpResponseRedirect(reverse('edit_location', args=[location.id]))
        location.enable_orders = True
    location.save()
    request.session['dashboard-location'] = location
    return HttpResponseRedirect(reverse('dashboard_orders'))
