from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, Http404
from django.utils import simplejson as json
from django.views.generic.simple import direct_to_template

import twilio

from tiger.sms.forms import CampaignForm, SettingsForm
from tiger.sms.models import SmsSubscriber, SMS
from tiger.utils.views import add_edit_site_object, delete_site_object


def respond_to_sms(request):
    utils = twilio.Utils(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_ACCOUNT_TOKEN)
    if not utils.validateRequest(request.site.tiger_domain() + reverse('respond_to_sms'), request.POST, request.META['HTTP_X_TWILIO_SIGNATURE']):
        return HttpResponseForbidden()
    sms_settings = request.site.sms
    body = request.POST.get('Body', '')
    normalized_body = body.strip().lower()
    phone_number = request.POST.get('From')
    try:
        subscriber = SmsSubscriber.objects.get(settings=sms_settings, phone_number=phone_number)
    except SmsSubscriber.DoesNotExist:
        if normalized_body == 'in':
            subscriber = SmsSubscriber.objects.create(
                settings=sms_settings,
                phone_number=phone_number,
                city=request.POST.get('FromCity', ''),
                state=request.POST.get('FromState', ''),
                zip_code=request.POST.get('FromZip', '')
            )
        else:
            subscriber = None
    SMS.objects.create(
        settings=sms_settings, 
        subscriber=subscriber, 
        destination=SMS.DIRECTION_INBOUND,
        body=body
    )
    return HttpResponse('<Response></Response>', mimetype='text/xml')


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

@login_required
@not_suspended
def sms_home(request):
    sms = request.site.sms
    if not sms.enabled:
        return sms_signup(request)
    try:
        in_progress = sms.campaign_set.filter(completed=False)[0]
    except IndexError:
        in_progress = None
    num = sms.sms_number
    sms_number = '(%s) %s-%s' % (num[2:5], num[5:8], num[8:])
    count_dict = {
        'total': sms.smssubscriber_set.all().count(),
        'active': sms.smssubscriber_set.active().count(),
        'inactive': sms.smssubscriber_set.inactive().count()
    }
    campaigns = sms.campaign_set.order_by('-timestamp')[:3]
    return direct_to_template(request, template='dashboard/marketing/sms_home.html', extra_context={
        'in_progress': in_progress,
        'count': count_dict,
        'sms': sms,
        'campaigns': campaigns
    })


@login_required
@not_suspended
def sms_signup(request):
    account = twilio.Account(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_ACCOUNT_TOKEN)
    site = request.site
    if request.method == 'POST':
        number = request.POST.get('number')
        response = account.request(
            '/2010-04-01/Accounts/%s/IncomingPhoneNumbers.json' % settings.TWILIO_ACCOUNT_SID, 
            'POST', 
            dict(
                PhoneNumber=number, 
                FriendlyName=site.name, 
                SmsUrl=site.tiger_domain() + reverse('respond_to_sms')
        ))
        data = json.loads(response)
        sms_settings = site.sms
        sms_settings.sid = data['sid']
        sms_settings.sms_number = data['phone_number']
        sms_settings.save()
        request.site.account.set_sms_subscription(True)
        return HttpResponseRedirect(reverse('sms_home'))
    else:
        area_code = request.GET.get('area_code') or request.site.location_set.all()[0].phone[:3]
        response = account.request('/2010-04-01/Accounts/%s/AvailablePhoneNumbers/us/Local.json' % settings.TWILIO_ACCOUNT_SID, 'GET', dict(AreaCode=area_code))
        data = json.loads(response)
        available_numbers = [
            (number['phone_number'], number['friendly_name'])
            for number in data['available_phone_numbers']
        ]
    return direct_to_template(request, template='dashboard/marketing/sms_signup.html', extra_context={ 'available_numbers': available_numbers,
        'area_code': area_code
    })


@login_required
@not_suspended
def sms_disable(request):
    account = twilio.Account(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_ACCOUNT_TOKEN)
    if request.method == 'POST':
        sms = request.site.sms
        response = account.request(
            '/2010-04-01/Accounts/%s/IncomingPhoneNumbers/%s' % (settings.TWILIO_ACCOUNT_SID, sms.sid), 
            'DELETE' 
        )
        sms.sms_number = sms.sid = None
        sms.save()
        request.site.account.set_sms_subscription(False)
        messages.success(request, "Your SMS number has been disabled.")
        return HttpResponseRedirect(reverse('sms_home'))
    else:
        return direct_to_template(request, template='dashboard/marketing/disable_sms.html')


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


@login_required
@not_suspended
def sms_subscriber_list(request):
    subscribers = request.site.sms.smssubscriber_set.active()
    return direct_to_template(request, template='dashboard/marketing/sms_subscriber_list.html', extra_context={
        'subscribers': subscribers
    })


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
        form = CampaignForm(request.POST)
        if form.is_valid():
            campaign = form.save(commit=False)
            campaign.settings = request.site.sms
            campaign.save()
            campaign.set_subscribers()
            campaign.queue()
            messages.success(request, """
<span>Campaign "%s" currently in progress. (<span class="sent-count">%d</span> / %d sent)</span>
            """ % (campaign.title, campaign.sent_count, campaign.count))
            return HttpResponseRedirect(reverse('sms_home'))
    else:
        form = CampaignForm()
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
def send_single_sms(request, subscriber_id):
    if request.method == 'POST':
        try:
            subscriber = request.site.sms.smssubscriber_set.get(id=subscriber_id)
        except SmsSubscriber.DoesNotExist:
            raise Http404
        subscriber.send_message(request.POST['text'][:160])
        messages.success(request, "SMS sent successfully.")
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    else:
        return direct_to_template(request, template='dashboard/marketing/includes/single_sms_form.html', extra_context={
            'subscriber_id': subscriber_id
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
        if form.is_valid():
            form.save()
            messages.success(request, "Settings updated successfully.")
            return HttpResponseRedirect(reverse('sms_home'))
    else:
        form = SettingsForm(instance=sms)
    return direct_to_template(request, template='dashboard/marketing/sms_settings.html', extra_context={
        'form': form
    })

@login_required
@not_suspended
def campaign_list(request):
    sms = request.site.sms
    campaigns = sms.campaign_set.order_by('-timestamp')
    return direct_to_template(request, template='dashboard/marketing/sms_campaign_list.html', extra_context={
        'campaigns': campaigns
    })
