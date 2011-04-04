import json

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.simple import direct_to_template
from django.shortcuts import get_object_or_404

from tiger.utils.cache import KeyChain
from tiger.stork import Stork
from tiger.stork.models import Theme


@login_required
def picker(request):
    request.session['customizing'] = True
    return HttpResponseRedirect('/')

@login_required
def back(request):
    request.session['customizing'] = False
    return HttpResponseRedirect(reverse('dashboard_content'))

@login_required
def theme_list(request):
    return direct_to_template(request, 'dashboard/look/theme_list.html', {
        'themes': Theme.objects.filter(private=False)
    })

@login_required
def theme_detail(request, theme_id):
    site = request.site
    theme = get_object_or_404(Theme, id=theme_id, private=False)
    if request.method == 'POST':
        old_theme = site.theme
        old_theme.delete()
        new_theme = Theme.objects.create()
        Stork(theme).copy_to(new_theme)
        site.theme = new_theme
        site.save()
        # trigger cache refresh
        new_theme.save()
        messages.success(request, "Theme changed successfully.  <a href='/'>Have a look</a> or <a href='%s'>Start customizing it!</a>" % reverse('dashboard_look'))
        return HttpResponseRedirect(reverse('theme_list'))
    return direct_to_template(request, 'dashboard/look/theme_detail.html', {
        'theme': theme
    })
