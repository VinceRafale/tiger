import re

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.utils import simplejson as json
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.views.generic.simple import direct_to_template

import twilio

from tiger.sms.forms import CampaignForm, SettingsForm
from tiger.sms.models import SmsSubscriber, SMS, Thread, Campaign
from tiger.sms.sender import Sender


def not_suspended(func):
    def wrapped(request, *args, **kwargs):
        if request.site.is_suspended:
            messages.error(request, 'Your account has been suspended because we were unable to process your credit card.  Currently, only fax and SMS functionality have been disabled.  You must update your billing information by first of the coming month or you will also lose the ability to update the site.')
            if request.site.managed:
                redirect_to = reverse('dashboard_marketing')
            else:
                redirect_to = reverse('update_cc')
            return HttpResponseRedirect(redirect_to)
        return func(request, *args, **kwargs)
    return wrapped


class SmsView(TemplateView):
    def get_sms_module(self):
        return self.request.site.sms


class AccountCheckView(object):
    @method_decorator(login_required)
    @method_decorator(not_suspended)
    def dispatch(self, *args, **kwargs):
        return super(AccountCheckView, self).dispatch(*args, **kwargs)


class SmsHomeBase(SmsView):
    template_name = 'dashboard/marketing/sms_home.html'
    redirect_to = 'sms_signup'

    def get(self, request, *args, **kwargs):
        sms = self.get_sms_module()
        if not sms.enabled:
            return HttpResponseRedirect(reverse(self.redirect_to))
        return super(SmsHomeBase, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = {}
        sms = self.get_sms_module()
        try:
            in_progress = sms.campaign_set.filter(completed=False)[0]
        except IndexError:
            in_progress = None
        num = sms.sms_number
        count_dict = {
            'total': sms.smssubscriber_set.all().count(),
            'active': sms.smssubscriber_set.active().count(),
            'inactive': sms.smssubscriber_set.inactive().count()
        }
        campaigns = sms.campaign_set.order_by('-timestamp')[:3]
        context.update({
            'in_progress': in_progress,
            'count': count_dict,
            'sms': sms,
            'campaigns': campaigns,
            'inbox': SMS.objects.inbox_for(sms)[:5],
            'list_counts': SmsSubscriber.objects.counts_per_tag(sms)
        })
        return context


class SmsSignupBase(SmsView):
    template_name = 'dashboard/marketing/sms_signup.html'

    def account(self):
        return twilio.Account(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_ACCOUNT_TOKEN)

    def get_sms_name(self):
        return self.request.site.name

    def get_sms_url(self):
        return self.request.site.tiger_domain() + reverse('respond_to_sms')

    def post(self, request, *args, **kwargs):
        number = request.POST.get('number')
        response = self.account().request(
            '/2010-04-01/Accounts/%s/IncomingPhoneNumbers.json' % settings.TWILIO_ACCOUNT_SID, 
            'POST', 
            dict(
                PhoneNumber=number, 
                FriendlyName=self.get_sms_name(), 
                SmsUrl=self.get_sms_url()
        ))
        data = json.loads(response)
        sms_settings = self.get_sms_module()
        sms_settings.sid = data['sid']
        sms_settings.sms_number = data['phone_number']
        sms_settings.save()
        return HttpResponseRedirect(reverse('sms_home'))

    def get_area_code(self):
        return self.request.site.location_set.all()[0].phone[:3]

    def get_context_data(self, **kwargs):
        context = super(SmsSignupBase, self).get_context_data(**kwargs)
        area_code = self.request.GET.get('area_code') or self.get_area_code()
        try:
            response = self.account().request('/2010-04-01/Accounts/%s/AvailablePhoneNumbers/US/Local.json' % settings.TWILIO_ACCOUNT_SID, 'GET', dict(AreaCode=area_code))
        except:
            available_numbers = []
        else:
            data = json.loads(response)
            available_numbers = [
                (number['phone_number'], number['friendly_name'])
                for number in data['available_phone_numbers']
            ]
        context.update({
            'available_numbers': available_numbers,
            'area_code': area_code
        })
        return context


class SmsDisableBase(SmsView):
    template_name = 'dashboard/marketing/disable_sms.html'

    def post(self, request, *args, **kwargs):
        account = twilio.Account(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_ACCOUNT_TOKEN)
        if request.method == 'POST':
            sms = request.site.sms
            account.request(
                '/2010-04-01/Accounts/%s/IncomingPhoneNumbers/%s' % (settings.TWILIO_ACCOUNT_SID, sms.sid), 
                'DELETE' 
            )
            sms.sms_number = sms.sid = None
            sms.save()
            messages.success(request, "Your SMS number has been disabled.")
            return HttpResponseRedirect(reverse('sms_home'))


@login_required
@not_suspended
def reorder_keywords(request):
    sms = request.site.sms
    new_keywords = request.POST.getlist('keywords')
    if set(new_keywords) == set(sms.keywords):
        sms.keywords = new_keywords
        sms.save()
    return HttpResponse('ok')

@login_required
@not_suspended
def remove_subscriber(request, subscriber_id):
    try:
        assert request.POST['delete']
        subscriber = request.site.sms.smssubscriber_set.get(id=subscriber_id)
    except (SmsSubscriber.DoesNotExist, KeyError):
        raise Http404
    subscriber.delete()
    return HttpResponse("deleted");


class SubscriberListView(SmsView, AccountCheckView):
    template_name = 'dashboard/marketing/sms_subscriber_list.html'

    def get_context_data(self, **kwargs):
        return {
            'subscribers': self.request.site.sms.smssubscriber_set.active()
        }


@login_required
@not_suspended
def toggle_star(request, subscriber_id):
    try:
        subscriber = request.site.sms.smssubscriber_set.get(id=subscriber_id)
    except SmsSubscriber.DoesNotExist:
        raise Http404
    subscriber.starred = not subscriber.starred
    subscriber.save()
    return HttpResponse('Favourite_24x24' if subscriber.starred else 'unstarred')


@login_required
@not_suspended
def create_campaign(request):
    if request.method == 'POST':
        form = CampaignForm(request.POST, site=request.site)
        if form.is_valid():
            campaign = form.save(commit=False)
            campaign.settings = request.site.sms
            tag = form.cleaned_data.get('keyword')
            if tag is not None:
                campaign.keyword = tag
            else:
                campaign.keyword = request.site.sms.keywords[0]
            campaign.save()
            campaign.set_subscribers()
            campaign.queue()
            messages.success(request, """
<span>Campaign "%s" currently in progress. (<span class="sent-count">%d</span> / %d sent)</span>
            """ % (campaign.title, campaign.sent_count, campaign.count))
            return HttpResponseRedirect(reverse('sms_home'))
    else:
        form = CampaignForm(site=request.site)
    return direct_to_template(request, template='dashboard/marketing/sms_campaign_form.html', extra_context={
        'form': form
    })


@login_required
@not_suspended
def get_options(request):
    attr_to_query = request.GET.get('attr')
    if not attr_to_query or attr_to_query not in ('city', 'state', 'zip_code'):
        raise Http404
    return HttpResponse(request.site.sms.get_options_for(attr_to_query))


@login_required
@not_suspended
def send_single_sms(request, phone_number):
    if request.method == 'POST':
        try:
            subscriber = request.site.sms.smssubscriber_set.get(phone_number=phone_number)
        except SmsSubscriber.DoesNotExist:
            subscriber = None
        if subscriber is not None and not subscriber.is_active:
            raise Http404
        sender = Sender(request.site, request.POST['text'])
        sender.add_recipients(subscriber or phone_number)
        sender.send_message()
        messages.success(request, "SMS sent successfully.")
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    else:
        return direct_to_template(request, template='dashboard/marketing/includes/single_sms_form.html', extra_context={
            'subscriber_id': phone_number
        })

@login_required
@not_suspended
def campaign_progress(request, campaign_id):
    try:
        campaign = request.site.sms.campaign_set.get(id=campaign_id)
    except Campaign.DoesNotExist:
        raise Http404
    return HttpResponse(json.dumps({
        'completed': campaign.completed,
        'count': campaign.sent_count
    }))

@login_required
@not_suspended
def edit_settings(request):
    sms = request.site.sms
    if request.method == 'POST':
        form = SettingsForm(request.POST, instance=sms)
        if 'remove' in request.POST:
            if len(sms.keywords) == 1:
                messages.error(request, "You must have at least one keyword.")
            else:
                sms.remove_keywords(request.POST.get('remove'))
                messages.success(request, "Keyword removed successfully.")

        elif 'add' in request.POST:
            add_word = request.POST.get('add')
            if re.match(r'[a-zA-Z0-9 ]+$', add_word):
                sms.add_keywords(add_word)
                messages.success(request, "Keyword added successfully.")
            else:
                messages.error(request, "Keywords may contain only letters, numbers, and spaces.")
        else:
            if form.is_valid():
                form.save()
                messages.success(request, "Settings updated successfully.")
                return HttpResponseRedirect(reverse('sms_home'))
    form = SettingsForm(instance=sms)
    return direct_to_template(request, template='dashboard/marketing/sms_settings.html', extra_context={
        'form': form,
        'sms': sms
    })

@login_required
@not_suspended
def campaign_list(request):
    sms = request.site.sms
    campaigns = sms.campaign_set.order_by('-timestamp')
    return direct_to_template(request, template='dashboard/marketing/sms_campaign_list.html', extra_context={
        'campaigns': campaigns
    })

@login_required
def inbox(request):
    return direct_to_template(request, template='dashboard/marketing/sms_inbox.html', extra_context={
        'inbox': SMS.objects.inbox_for(request.site.sms),
        'sms': request.site.sms
    })


@login_required
def thread_detail(request, phone_number):
    Thread.objects.filter(phone_number=phone_number).update(unread=False)
    try:
        subscriber = SmsSubscriber.objects.get(settings=request.site.sms, phone_number=phone_number)
    except SmsSubscriber.DoesNotExist:
        subscriber = None
    return direct_to_template(request, template='dashboard/marketing/sms_thread.html', extra_context={
        'number': phone_number,
        'thread': SMS.objects.thread_for(settings=request.site.sms, phone_number=phone_number),
        'subscriber': subscriber
    })


class SmsHomeView(AccountCheckView, SmsHomeBase):
    pass


class SmsSignupView(AccountCheckView, SmsSignupBase):
    pass


class SmsDisableView(AccountCheckView, SmsDisableBase):
    pass
