import json

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.simple import direct_to_template

from tiger.utils.cache import KeyChain


@login_required
def picker(request):
    request.session['customizing'] = True
    return HttpResponseRedirect('/')

@login_required
def back(request):
    request.session['customizing'] = False
    return HttpResponseRedirect(reverse('dashboard_content'))
