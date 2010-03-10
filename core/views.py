from datetime import datetime

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.http import base36_to_int
from django.shortcuts import get_object_or_404, render_to_response
from django.template.defaultfilters import slugify

from tiger.core.forms import get_order_form, OrderForm, CouponForm
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
    return render_custom(request, 'core/item_detail.html', 
        {'item': i, 'sections': request.site.section_set.all()})

def order_item(request, section, item):
    i = get_object_or_404(Item, section__slug=section, slug=item, site=request.site)
    if not request.site.enable_orders:
        return HttpResponseRedirect(i.get_absolute_url())
    if not i.available:
        msg = """%s is currently not available. Please try one of our other
        menu items.""" % i.name
        messages.warning(request, msg) 
        return HttpResponseRedirect(i.section.get_absolute_url())
    OrderForm = get_order_form(i)
    total = i.variant_set.order_by('-price')[0].price
    if request.method == 'POST':
        if not request.site.is_open:
            msg = """%s is currently closed. Please try ordering during normal
            restaurant hours, %s.""" % (request.site.name, request.site.hours)
            messages.warning(request, msg) 
            return HttpResponseRedirect(i.section.get_absolute_url())
        if not i.available:
            msg = """%s is currently not available. Please try one of our other
            menu items.""" % i.name
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
    return render_custom(request, 'core/order_form.html', {'item': i, 'form': form, 'total': total, 'sections': request.site.section_set.all()})

def preview_order(request):
    if request.method == 'POST':
        form = CouponForm(request.site, request.POST)
        if request.cart.has_coupon:
            messages.error(request, 'You have already added coupon to this order.')   
        elif form.is_valid():
            coupon = form.coupon
            request.cart.add_coupon(coupon)
            return HttpResponseRedirect(reverse('preview_order'))
    else:
        if request.cart.has_coupon:
            form = None
        else:
            form = CouponForm()
    return render_custom(request, 'core/preview_order.html', 
        {'form': form})

def remove_item(request):
    request.cart.remove(request.GET.get('id'))
    return HttpResponseRedirect(reverse('preview_order'))

def send_order(request):
    now = datetime.now()
    # filter initial time values to exclude all times not during working hours
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.total = request.cart.total()
            order.cart = request.cart.session.get_decoded()
            order.site = request.site
            order.save()
            if request.cart.has_coupon:
                coupon = Coupon.objects.get(id=request.cart['coupon']['id'])
                coupon.log_use(order)
            content = render_to_pdf('notify/order.html', {
                'data': form.cleaned_data,
                'cart': request.cart,
                'order_no': order.id,
                'method': order.get_method_display()
            })
            SendFaxTask.delay(request.site, request.site.fax_number, content, IsFineRendering=True)
            request.cart.clear()
            return HttpResponseRedirect(reverse('order_success'))
    else:
        form = OrderForm()
    return render_custom(request, 'core/send_order.html', {'form': form})

def order_success(request):
    return render_custom(request, 'core/order_success.html')

def download_menu(request):
    menu = request.site.menu
    if menu is None:
        return HttpResponseRedirect(reverse('section_detail'))
    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = 'filename=%s.pdf' % slugify(request.site.name)
    response.write(menu.render())
    return response
