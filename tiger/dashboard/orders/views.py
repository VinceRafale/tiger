from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic.simple import direct_to_template

from tiger.core.forms import OrderSettingsForm
from tiger.core.models import Order

def home(request):
    return direct_to_template(request, template='dashboard/orders/home.html', extra_context={
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
            options = form.save()
            messages.success(request, 'Your order options have been updated.')
            return HttpResponseRedirect(reverse('dashboard_orders'))
    else:
        form = OrderSettingsForm(site=request.site, instance=request.site.ordersettings)
    return direct_to_template(request, template='dashboard/orders/order_options.html', extra_context={
        'form': form
    })
