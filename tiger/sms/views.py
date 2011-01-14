from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, Http404
from django.utils import simplejson as json
from django.views.generic.simple import direct_to_template

import twilio

from tiger.sms.models import SmsSubscriber, SMS
from tiger.utils.views import add_edit_site_object, delete_site_object


def respond_to_sms(request):
    utils = twilio.Utils(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_ACCOUNT_TOKEN)
    if not utils.validateRequest(request.site.tiger_domain + reverse('respond_to_sms'), request.POST, request.META['X_HTTP_TWILIO_SIGNATURE']):
        return HttpResponseForbidden()
    sms_settings = request.site.sms
    body = request.POST.get('Body', '')
    normalized_body = body.strip().lower()
    phone_number = request.POST.get('From')
    subscriber, created = SmsSubscriber.objects.get_or_create(
        settings=sms_settings,
        phone_number=phone_number, defaults=dict(
            city=request.POST.get('FromCity', ''),
            state=request.POST.get('FromState', ''),
            zip_code=request.POST.get('FromZip', ''),
        )
    )
    SMS.objects.create(
        settings=sms_settings, 
        subscriber=subscriber, 
        direction=SMS.DIRECTION_INBOUND,
        body=body
    )
    if normalized_body == 'in' and created:
        # add subscription
        if sms_settings.send_intro:
            subscriber.send_message(sms_settings.intro_text)
    elif normalized_body == 'out':
        subscriber.unsubscribed_at = datetime.now()
        subscriber.save()
    return HttpResponse('<Response></Response>', mimetype='text/xml')


def sms_home(request):
    if not request.site.sms.enabled:
        return sms_signup(request)
    return direct_to_template(request, template='dashboard/marketing/sms_home.html', extra_context={
    })


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
        return HttpResponseRedirect(reverse('sms_home'))
    else:
        area_code = request.GET.get('area_code') or request.site.location_set.all()[0].phone[:3]
        response = account.request('/2010-04-01/Accounts/%s/AvailablePhoneNumbers/us/Local.json' % settings.TWILIO_ACCOUNT_SID, 'GET', dict(AreaCode=area_code))
        data = json.loads(response)
        available_numbers = [
            (number['phone_number'], number['friendly_name'])
            for number in data['available_phone_numbers']
        ]
    return direct_to_template(request, template='dashboard/marketing/sms_signup.html', extra_context={
        'available_numbers': available_numbers,
        'area_code': area_code
    })


def sms_disable(request):
    if not request.POST.get('disable'):
        raise Http404
    sms = request.site.sms
    sms.sms_number = sms.sid = None
    sms.save()
    messages.success(request, "Your SMS number has been disabled.")
    return HttpResponseRedirect(reverse('sms_home'))


def remove_subscriber(request, subscriber_id):
    try:
        assert request.POST['delete']
        subscriber = request.site.sms.smssubscriber_set.get(id=subscriber_id)
    except (SmsSubscriber.DoesNotExist, KeyError):
        raise Http404
    subscriber.delete()
    return HttpResponse("deleted");


def sms_subscriber_list(request):
    subscribers = request.site.sms.smssubscriber_set.active()
    return direct_to_template(request, template='dashboard/marketing/sms_subscriber_list.html', extra_context={
        'subscribers': subscribers
    })


def toggle_star(request, subscriber_id):
    try:
        subscriber = request.site.sms.smssubscriber_set.get(id=subscriber_id)
    except SmsSubscriber.DoesNotExist:
        raise Http404
    subscriber.starred = not subscriber.starred
    subscriber.save()
    return HttpResponse('Favourite_24x24' if subscriber.starred else 'unstarred')


def send_sms(request):
    pass


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
