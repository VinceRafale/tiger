from decimal import InvalidOperation

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.core.validators import email_re
from django.forms.util import ErrorList
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404

from greatape import MailChimp
from paypal.standard.forms import PayPalPaymentsForm

from tiger.core.forms import get_order_form, OrderForm, CouponForm, AuthNetForm
from tiger.core.models import Section, Item, Coupon, Order
from tiger.notify.tasks import DeliverOrderTask
from tiger.utils.views import render_custom

def section_list(request):
    sections = Section.objects.filter(site=request.site)
    return render_custom(request, 'core/section_list.html', 
        {'sections': sections})

def section_detail(request, section):
    s = get_object_or_404(Section, slug=section, site=request.site)
    return render_custom(request, 'core/section_detail.html', 
        {'section': s})
    
def item_detail(request, section, item):
    i = get_object_or_404(Item, section__slug=section, slug=item, site=request.site)
    if i.price_list in (None, []):
        raise Http404
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
        section = i.section
        if not section.is_available:
            msg = 'Items from %s are only available %s.' % (
                section.name, section.hours)
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
    else:
        form = OrderForm()
    return render_custom(request, 'core/order_form.html', {'item': i, 'form': form, 'total': '%.2f' % total, 'sections': request.site.section_set.all()})

def preview_order(request):
    if request.method == 'POST':
        form = CouponForm(request.site, request.POST)
        if request.cart.has_coupon:
            messages.error(request, 'You have already added a coupon to this order.')   
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

def add_coupon(request):
    code = request.GET.get('cc')
    if code is None:
        raise Http404
    coupon = get_object_or_404(Coupon, id=code, site=request.site)
    if request.cart.has_coupon:
        messages.error(request, 'You already have a coupon in your cart.')   
    else:
        request.cart.add_coupon(coupon)
        messages.success(request, 'Coupon added to your cart successfully.')   
    return HttpResponseRedirect(reverse('menu_home'))

def send_order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST, site=request.site)
        form.total = request.cart.total()
        if form.is_valid():
            order = form.save(commit=False)
            order.total = request.cart.total()
            order.tax = request.cart.taxes()
            order.cart = request.cart.session.get_decoded()
            order.site = request.site
            try:
                order.save()
            except InvalidOperation:
                form._errors['__all__'] = ErrorList(['Your order is too large.  Please contact us for catering options.'])
            else:
                if request.cart.has_coupon:
                    coupon = Coupon.objects.get(id=request.cart['coupon']['id'])
                    coupon.log_use(order)
                if 'pay' in request.POST:
                    request.session['order_id'] = order.id
                    return HttpResponseRedirect(
                        request.site.ordersettings.payment_url(
                            cart_id=request.cart.session.session_key,
                            order_id=order.id
                        )
                    )
                DeliverOrderTask.delay(order.id, Order.STATUS_SENT)
                request.cart.clear()
                return HttpResponseRedirect(reverse('order_success'))
    else:
        form = OrderForm(site=request.site)
    context = {
        'form': form
    }
    return render_custom(request, 'core/send_order.html', context)

def payment_paypal(request):
    try:
        Order.objects.get(id=request.session['order_id'])
    except (Order.DoesNotExist, KeyError):
        return HttpResponseRedirect(reverse('preview_order'))
    request.cart.clear()
    site = request.site
    domain = str(site)
    paypal_dict = {
        'business': site.ordersettings.paypal_email,
        'amount': request.cart.total,
        'invoice': request.session['order_id'],
        'item_name': 'Your order at %s' % site.name,
        'notify_url': domain + reverse('paypal-ipn'),
        'return_url': domain + reverse('order_success'),
        'cancel_return': domain + reverse('preview_order'),
    }
    form = PayPalPaymentsForm(initial=paypal_dict)
    context = {'form': form}
    return render_custom(request, 'core/payment_paypal.html', context)

def payment_authnet(request):
    order_id = request.REQUEST.get('o')
    try:
        order = Order.objects.get(id=order_id)
    except (Order.DoesNotExist, KeyError):
        return HttpResponseRedirect(reverse('preview_order'))
    if request.method == 'POST':
        form = AuthNetForm(request.POST, order=order)
        if form.is_valid():
            order.notify_restaurant(Order.STATUS_PAID)
            request.cart.clear()
            return HttpResponseRedirect(str(request.site) + reverse('order_success'))
    else:
        form = AuthNetForm(order=order)
    context = {'form': form, 'order_id': order_id, 'order_settings': request.site.ordersettings}
    return render_custom(request, 'core/payment_authnet.html', context)
            

def order_success(request):
    return render_custom(request, 'core/order_success.html')

def mailing_list_signup(request):
    email = request.POST.get('email')
    if email_re.match(email):
        social = request.site.social
        mailchimp = MailChimp(social.mailchimp_api_key)
        response = mailchimp.listSubscribe(
            id=social.mailchimp_list_id, 
            email_address=email,
            merge_vars=''
        )
        if response is True:
            success_msg = 'Thanks for signing up!  We\'ll send you a confirmation e-mail shortly.'
            messages.success(request, success_msg)
        else:
            messages.warning(request, 'We were unable to sign you up at this time.  Please try again.')
    else:
        error_msg = 'Please enter a valid e-mail address.'
        messages.error(request, error_msg)
    return HttpResponseRedirect(request.META['HTTP_REFERER'])
