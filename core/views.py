from datetime import datetime

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.http import base36_to_int
from django.shortcuts import get_object_or_404, render_to_response

from tiger.core.forms import get_order_form, OrderForm
from tiger.core.models import Section, Item
from tiger.notify.tasks import SendFaxTask
from tiger.utils.pdf import render_to_pdf
from tiger.utils.views import render_custom

def section_list(request):
    sections = Section.objects.filter(site=request.site)
    return render_custom(request, 'core/section_list.html', 
        {'sections': sections})

def section_detail(request, section):
    s = get_object_or_404(Section, slug=section, site=request.site)
    return render_custom(request, 'core/section_detail.html', 
        {'section': s})
    
def short_code(request, item_id):
    item_id = base36_to_int(item_id)
    item = get_object_or_404(Item, id=item_id, site=request.site)
    return HttpResponseRedirect(item.get_absolute_url())

def item_detail(request, section, item):
    i = get_object_or_404(Item, section__slug=section, slug=item, site=request.site)
    if request.method == 'POST':
        qty = request.POST.get('qty')
        request.cart.add(i.id, int(qty))
    return render_custom(request, 'core/item_detail.html', 
        {'item': i})

def order_item(request, section, item):
    i = get_object_or_404(Item, section__slug=section, slug=item, site=request.site)
    if not request.site.enable_orders:
        return HttpResponseRedirect(i.get_absolute_url())
    OrderForm = get_order_form(i)
    total = i.variant_set.order_by('-price')[0].price
    if request.method == 'POST':
        if not request.site.is_open:
            msg = """%s is currently closed. Please try ordering during normal
            restaurant hours, %s.""" % (request.site.name, request.site.hours)
            messages.warning(request, msg) 
            return HttpResponseRedirect(i.section.get_absolute_url())
        form = OrderForm(request.POST)
        if form.is_valid():
            request.cart.add(i, form)
            msg = """%s added to your order. You can 
            <a href="%s">complete your order now</a> or add more items.""" % (
                i.name, reverse('preview_order'))
            messages.success(request, msg) 
            return HttpResponseRedirect(i.section.get_absolute_url())
        print form._errors
    else:
        form = OrderForm()
    return render_custom(request, 'core/order_form.html', {'item': i, 'form': form, 'total': total})

def remove_item(request):
    request.cart.remove(request.GET.get('id'))
    return HttpResponseRedirect(reverse('preview_order'))

def send_order(request):
    now = datetime.now()
    # filter initial time values to exclude all times not during working hours
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # log the sale
            content = render_to_pdf('notify/order.html', {
                'data': form.cleaned_data,
                'cart': request.cart
            })
            SendFaxTask.delay(request.site, request.site.fax_number, content, IsFineRendering=True)
            request.cart.clear()
            return HttpResponseRedirect(reverse('order_success'))
    else:
        form = OrderForm()
    return render_custom(request, 'core/send_order.html', {'form': form})

def order_success(request):
    return  render_custom(request, 'core/order_success.html')
