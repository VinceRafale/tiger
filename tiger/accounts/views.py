from django.http import HttpResponseRedirect
from django.views.generic.simple import direct_to_template

from tiger.accounts.forms import SignupForm


def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            instance = form.save()
            return HttpResponseRedirect(unicode(instance.site) + reverse('dashboard'))
    else:
        form = SignupForm()
    return direct_to_template(request, template='tiger/signup.html', extra_context={
        'form': form
    })

