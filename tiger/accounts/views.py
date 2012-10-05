import json

from django.core.urlresolvers import reverse
from django.contrib.auth.views import password_reset as default_reset
from django.contrib.auth.forms import PasswordResetForm
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.views.generic.simple import direct_to_template
from django.shortcuts import get_object_or_404

from tiger.sales.forms import SiteSignupForm, SignupRedirectForm
from tiger.accounts.models import Site
from tiger.sales.models import Account, SalesRep
from tiger.utils.forms import SpanErrorList


def get_password_reset_form(request):
    class SitePasswordResetForm(PasswordResetForm):
        def save(self, *args, **kwargs):
            super(SitePasswordResetForm, self).save(domain_override=request.site.tiger_domain, *args, **kwargs)
    return SitePasswordResetForm


def password_reset(request, **kwargs):
    return default_reset(request, password_reset_form=get_password_reset_form(request), **kwargs)


def signup_redirect(request):
    if request.method == 'POST':
        form = SignupRedirectForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect(form.plan.signup_url())
    else:
        form = SignupRedirectForm
    return direct_to_template(request, template='tiger/signup_redirect.html', extra_context={
        'form': form
    })


def signup(request, reseller_secret, plan_secret):
    account = get_object_or_404(Account, secret=reseller_secret)
    plan = get_object_or_404(account.plan_set, secret=plan_secret)
    if request.method == 'POST':
        form = SiteSignupForm(request.POST, account=account, plan=plan, error_class=SpanErrorList)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(unicode(form.site) + reverse('dashboard', urlconf='tiger.urls'))
    else:
        form = SiteSignupForm(account=account, plan=plan)
    return direct_to_template(request, template='tiger/signup.html', extra_context={
        'form': form,
        'plan': plan
    })


def domain_check(request):
    if not request.is_ajax() or request.method != 'POST':
        raise Http404
    subdomain = request.POST.get('subdomain', '')
    data = {}
    try:
        Site.objects.get(subdomain=subdomain)
    except Site.DoesNotExist:
        data['available'] = True
    else:
        data['available'] = False
    return HttpResponse(json.dumps(data))


def validate_coupon(request):
    if not request.is_ajax() or request.method != 'POST':
        raise Http404
    code = request.POST.get('coupon', '')
    data = {}
    try:
        SalesRep.objects.get(code=code)
    except SalesRep.DoesNotExist:
        data['valid'] = True
    else:
        data['valid'] = False
    return HttpResponse(json.dumps(data))


def cancelled(request):
    return direct_to_template(request, template='tiger/cancelled.html')

def privacy(request):
    return direct_to_template(request, template='tiger/privacy.html')

def terms(request):
    return direct_to_template(request, template='tiger/terms.html')
