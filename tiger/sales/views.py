import re

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.views.decorators.csrf import csrf_protect
from django.views.generic.simple import direct_to_template

from tiger.accounts.models import Site
from tiger.sales.forms import (AuthenticationForm, CreateSiteForm, 
    CreatePlanForm, EditSiteForm, CreateResellerAccountForm, ImportMenuForm,)
from tiger.sales.models import Plan, Invoice


@csrf_protect
def login(request, redirect_field_name='next'):
    """Displays the login form and handles the login action."""
    redirect_to = request.REQUEST.get(redirect_field_name, '')
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            # Light security check -- make sure redirect_to isn't garbage.
            if not redirect_to or ' ' in redirect_to:
                redirect_to = settings.LOGIN_REDIRECT_URL
            # Heavier security check -- redirects to http://example.com should 
            # not be allowed, but things like /view/?param=http://example.com 
            # should be allowed. This regex checks if there is a '//' *before* a
            # question mark.
            elif '//' in redirect_to and re.match(r'[^\?]*//', redirect_to):
                    redirect_to = settings.LOGIN_REDIRECT_URL
            # Okay, security checks complete. Log the user in.
            auth_login(request, form.get_user())
            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()
            return HttpResponseRedirect(redirect_to)
    else:
        form = AuthenticationForm(request=request)
    request.session.set_test_cookie()
    return direct_to_template(request, template='sales/login.html', extra_context={
        'form': form, redirect_field_name: redirect_to,
    })

@csrf_protect
def signup(request):
    if request.method == 'POST':
        form = CreateResellerAccountForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('auth_login'))
    else:
        form = CreateResellerAccountForm()
    return direct_to_template(request, template='sales/signup.html', extra_context={'form': form})


@login_required
def home(request):
    account = request.user.get_profile()
    return direct_to_template(request, template='sales/home.html', extra_context={
        'account': account
    })

@login_required
def plan_list(request):
    plans = request.user.get_profile().plan_set.all()
    return direct_to_template(request, template='sales/plan_list.html', extra_context={
        'plans': plans
    })

@login_required
def create_plan(request, plan_id=None):
    account = request.user.get_profile()
    instance = None
    if plan_id is not None:
        try:
            instance = account.plan_set.get(id=plan_id)
        except Plan.DoesNotExist:
            raise Http404
    if request.method == 'POST':
        form = CreatePlanForm(request.POST, instance=instance)
        if form.is_valid():
            plan = form.save(commit=False)
            plan.account = account
            plan.save()
            messages.success(request, 'Plan %s successfully.' % 'edited' if instance else 'created')
            return HttpResponseRedirect(reverse('plan_list'))
    else:
        form = CreatePlanForm(instance=instance)
    return direct_to_template(request, template='sales/plan_form.html', extra_context={
        'form': form,
        'instance': instance
    })

@login_required
def delete_plan(request, plan_id):
    account = request.user.get_profile()
    try:
        plan = account.plan_set.get(id=plan_id)
    except Site.DoesNotExist:
        raise Http404
    if request.method == 'POST':
        if plan.site_set.count() > 0:
            messages.error(request, 'You still have restaurants on this plan.  Please change the plans for all restaurants before deleting this plan: <ul>%s</ul>' % ''.join('<li><a href="%s">%s</a></li>' % (reverse('edit_restaurant', args=[site.id]), site.name) for site in plan.site_set.all()))
        else:
            plan.delete()
            messages.success(request, 'Plan deleted successfully.')
            return HttpResponseRedirect(reverse('plan_list'))
    return direct_to_template(request, template='sales/delete_plan.html', extra_context={
        'plan': plan
    })

@login_required
def restaurant_list(request):
    restaurants = request.user.get_profile().site_set.all()
    return direct_to_template(request, template='sales/restaurant_list.html', extra_context={
        'restaurants': restaurants
    })

@login_required
def create_edit_restaurant(request, restaurant_id=None):
    account = request.user.get_profile()
    instance = None
    RestaurantForm = CreateSiteForm
    if restaurant_id is not None:
        try:
            instance = account.site_set.get(id=restaurant_id)
        except Site.DoesNotExist:
            raise Http404
        RestaurantForm = EditSiteForm
    if request.method == 'POST':
        form = RestaurantForm(request.POST, account=account, instance=instance)
        if form.is_valid():
            restaurant = form.save(commit=False)
            restaurant.managed = True
            restaurant.save()
            restaurant.send_confirmation_email()
            messages.success(request, 'Restaurant %s successfully.' % ('edited' if instance else 'created'))
            return HttpResponseRedirect(reverse('restaurant_list'))
    else:
        form = RestaurantForm(account=account, instance=instance)
    return direct_to_template(request, template='sales/restaurant_form.html', extra_context={
        'form': form,
        'instance' : instance
    })

@login_required
def restaurant_detail(request, site_id):
    account = request.user.get_profile()
    try:
        restaurant = account.site_set.get(id=site_id)
    except Site.DoesNotExist:
        raise Http404
    return direct_to_template(request, template='sales/restaurant_detail.html', extra_context={
        'restaurant': restaurant
    })

@login_required
def delete_restaurant(request, site_id):
    account = request.user.get_profile()
    try:
        restaurant = account.site_set.get(id=site_id)
    except Site.DoesNotExist:
        raise Http404
    if request.method == 'POST':
        restaurant.user.delete()
        restaurant.delete()
        messages.success(request, 'Restaurant deleted successfully.')
        return HttpResponseRedirect(reverse('restaurant_list'))
    return direct_to_template(request, template='sales/delete_restaurant.html', extra_context={
        'restaurant': restaurant
    })

@login_required
def billing_home(request):
    account = request.user.get_profile()
    return direct_to_template(request, template='sales/billing_home.html', extra_context={
        'invoices': account.invoice_set.filter(invoice__isnull=True)
    })

@login_required
def invoice_detail(request, invoice_id):
    account = request.user.get_profile()
    try:
        invoice = account.invoice_set.get(id=invoice_id)
    except Invoice.DoesNotExist:
        raise Http404
    return direct_to_template(request, template='sales/invoice_detail.html', 
        extra_context={'invoice': invoice})

@login_required
def email_restaurant(request, site_id):
    if request.method != 'POST':
        raise Http404
    account = request.user.get_profile()
    try:
        restaurant = account.site_set.get(id=site_id)
    except Site.DoesNotExist:
        raise Http404
    restaurant.send_confirmation_email()
    messages.success(request, 'E-mail sent.')
    return HttpResponseRedirect(reverse('restaurant_detail', args=[site_id]))

@login_required
def import_menu(request, site_id):
    account = request.user.get_profile()
    try:
        restaurant = account.site_set.get(id=site_id)
    except Site.DoesNotExist:
        raise Http404
    if request.method == "POST":
        form = ImportMenuForm(request.POST, request.FILES, instance=restaurant)
        if form.is_valid():
            messages.success(request, 'Menu imported successfully.')
            return HttpResponseRedirect(reverse('restaurant_detail', args=[site_id]))
    else:
        form = ImportMenuForm(instance=restaurant)
    return direct_to_template(request, template='sales/import_menu.html', extra_context={
        'form': form
    })
