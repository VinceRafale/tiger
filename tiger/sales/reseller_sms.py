from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.views.generic.simple import direct_to_template

from tiger.sms.views import SmsHomeBase, SmsSignupBase, SmsDisableBase
from tiger.sms.forms import SettingsForm


class SmsHomeView(SmsHomeBase):
    template_name = 'sales/sms_home.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(SmsHomeView, self).dispatch(*args, **kwargs)

    def get_sms_module(self):
        return self.request.user.get_profile().sms


class SmsSignupView(SmsSignupBase):
    template_name = 'sales/sms_signup.html'

    def get_area_code(self):
        return '413'

    def get_sms_name(self):
        return self.request.user.get_profile().company_name

    def get_sms_url(self):
        return 'https://www.takeouttiger.com' + reverse('reseller_sms_subscribe', args=[self.request.user.get_profile().id], urlconf='tiger.tiger_urls')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(SmsSignupBase, self).dispatch(*args, **kwargs)

    def get_sms_module(self):
        return self.request.user.get_profile().sms


class SmsDisableView(SmsDisableBase):
    template_name = 'sales/sms_disable.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(SmsDisableBase, self).dispatch(*args, **kwargs)

    def get_sms_module(self):
        return self.request.user.get_profile().sms


class SubscriberListView(TemplateView):
    template_name = 'sales/sms_subscriber_list.html'

    def get_context_data(self, **kwargs):
        return {
            'subscribers': self.request.user.get_profile().sms.smssubscriber_set.active()
        }

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(TemplateView, self).dispatch(*args, **kwargs)

    def get_sms_module(self):
        return self.request.user.get_profile().sms


@login_required
def edit_settings(request):
    sms = request.user.get_profile().sms
    if request.method == 'POST':
        form = SettingsForm(request.POST, instance=sms)
        if form.is_valid():
            form.save()
            messages.success(request, "Settings updated successfully.")
            return HttpResponseRedirect(reverse('sms_home'))
    else:
        form = SettingsForm(instance=sms)
    return direct_to_template(request, template='sales/sms_settings.html', extra_context={
        'form': form,
        'sms': sms
    })
