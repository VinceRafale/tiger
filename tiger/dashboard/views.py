import re

from django.conf import settings
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.views.decorators.csrf import csrf_protect
from django.views.generic.simple import direct_to_template

from tiger.accounts.models import Location
from tiger.dashboard.forms import AuthenticationForm


@csrf_protect
def login(request, redirect_field_name='next'):
    """Displays the login form and handles the login action."""

    redirect_to = request.REQUEST.get(redirect_field_name, '')
    
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST, site=request.site)
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
    
    return direct_to_template(request, template='dashboard/login.html', extra_context={
        'form': form,
        redirect_field_name: redirect_to,
    })


@login_required
def dashboard(request):
    return HttpResponseRedirect(reverse('dashboard_menu'))

@login_required
def change_location(request):
    if not request.method == 'POST':
        raise Http404
    location_id = request.POST.get('loc')
    request.session['dashboard-location'] = request.site.location_set.get(id=location_id)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER') or '/dashboard/menu/')
