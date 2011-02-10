import re

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_protect
from django.views.generic.simple import direct_to_template

from tiger.sales.forms import AuthenticationForm, CreateSiteForm, CreatePlanForm


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
        'form': form,
        redirect_field_name: redirect_to,
    })

def home(request):
    return direct_to_template(request, template='sales/home.html', extra_context={
    })

def plan_list(request):
    plans = request.user.get_profile().plan_set.all()
    return direct_to_template(request, template='sales/plan_list.html', extra_context={
        'plans': plans
    })

def create_plan(request):
    account = request.user.get_profile()
    if request.method == 'POST':
        form = CreatePlanForm(request.POST)
        if form.is_valid():
            plan = form.save(commit=False)
            plan.account = account
            plan.save()
            messages.success(request, 'Plan created successfully.')
            return HttpResponseRedirect(reverse('plan_list'))
    else:
        form = CreatePlanForm()
    return direct_to_template(request, template='sales/plan_form.html', extra_context={
        'form': form
    })

def restaurant_list(request):
    restaurants = request.user.get_profile().site_set.all()
    return direct_to_template(request, template='sales/restaurant_list.html', extra_context={
        'restaurants': restaurants
    })

def create_restaurant(request):
    account = request.user.get_profile()
    if request.method == 'POST':
        form = CreateSiteForm(request.POST, account=account)
    else:
        form = CreateSiteForm(account=account)
    return direct_to_template(request, template='sales/restaurant_form.html', extra_context={
        'form': form
    })

def restaurant_detail(request, site_id):
    pass

def billing_home(request):
    pass
