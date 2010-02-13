from django.http import HttpResponse, HttpResponseRedirect
from django.utils.http import base36_to_int
from django.shortcuts import get_object_or_404, render_to_response

from tiger.core.forms import get_order_form
from tiger.core.models import Section, Item
from tiger.utils.views import render_custom

def section_list(request):
    sections = Section.objects.filter(site=request.site)
    return HttpResponse(render_custom(request, 'core/section_list.html', 
        {'sections': sections}))

def section_detail(request, section):
    s = get_object_or_404(Section, slug=section, site=request.site)
    return HttpResponse(render_custom(request, 'core/section_detail.html', 
        {'section': s}))

def item_detail(request, section, item):
    i = get_object_or_404(Item, section__slug=section, slug=item, site=request.site)
    if request.method == 'POST':
        qty = request.POST.get('qty')
        request.cart.add(i.id, int(qty))
    return HttpResponse(render_custom(request, 'core/item_detail.html', 
        {'item': i}))

def order_item(request, section, item):
    i = get_object_or_404(Item, section__slug=section, slug=item, site=request.site)
    OrderForm = get_order_form(i, i.variant_set.all(), i.upgrade_set.all())
    if request.method == 'POST':
        form = OrderForm(request.POST)
    else:
        form = OrderForm()
        total = i.variant_set.order_by('-price')[0].price
    return HttpResponse(render_custom(request, 'core/order_form.html', {'item': i, 'form': form, 'total': total}))

def short_code(request, item_id):
    item_id = base36_to_int(item_id)
    item = get_object_or_404(Item, id=item_id, site=request.site)
    return HttpResponseRedirect(item.get_absolute_url())
