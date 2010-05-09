import json

from django.contrib.auth import login, authenticate
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.views.generic.simple import direct_to_template

from tiger.accounts.forms import SignupForm
from tiger.accounts.models import Site


def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            instance = form.save()
            return HttpResponseRedirect(unicode(form.site) + reverse('dashboard', urlconf='tiger.urls'))
    else:
        form = SignupForm()
    return direct_to_template(request, template='tiger/signup.html', extra_context={
        'form': form
    })


def domain_check(request):
    if not request.is_ajax() or request.method != 'POST':
        return Http404
    subdomain = request.POST.get('subdomain', '')
    data = {}
    try:
        site = Site.objects.get(subdomain=subdomain)
    except Site.DoesNotExist:
        data['available'] = True
    else:
        data['available'] = False
    return HttpResponse(json.dumps(data))


def validate_coupon(request):
    if not request.is_ajax() or request.method != 'POST':
        return Http404
    code = request.POST.get('coupon', '')
    data = {}
    try:
        rep = SalesRep.objects.get(code=code)
    except SalesRep.DoesNotExist:
        data['valid'] = True
    else:
        data['valid'] = False
    return HttpResponse(json.dumps(data))


def cancelled(request):
    return direct_to_template(request, template='tiger/cancelled.html')
