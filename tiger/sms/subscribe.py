from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden

import twilio

from tiger.sms.models import SmsSubscriber, SMS


class SubscriptionView(object):
    def absolute_url(self):
        return ''.join([
            'http%s://' % ('s' if self.request.META.get('HTTP_X_FORWARDED_PORT') == '443' else ''),
            self.get_host(),
            self.request.path
        ])

    def get_host(self):
        raise NotImplementedError

    def get_sms_settings(self):
        raise NotImplementedError 

    def matches_condition(self, keyword):
        raise NotImplementedError 

    def log_sms(self, subscriber, body, phone_number):
        raise NotImplementedError

    def __call__(self, request, *args, **kwargs):
        self.request = request
        utils = twilio.Utils(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_ACCOUNT_TOKEN)
        if not utils.validateRequest(self.absolute_url(), request.POST, request.META['HTTP_X_TWILIO_SIGNATURE']):
            return HttpResponseForbidden()
        self.settings = sms_settings = self.get_sms_settings()
        body = request.POST.get('Body', '')
        normalized_body = body.strip().lower()
        phone_number = request.POST.get('From')
        try:
            subscriber = SmsSubscriber.objects.get(settings=sms_settings, phone_number=phone_number)
        except SmsSubscriber.DoesNotExist:
            if self.matches_condition(normalized_body):
                subscriber = SmsSubscriber.objects.create(
                    settings=sms_settings,
                    phone_number=phone_number,
                    city=request.POST.get('FromCity', ''),
                    state=request.POST.get('FromState', ''),
                    zip_code=request.POST.get('FromZip', ''),
                    tag=normalized_body
                )
            else:
                subscriber = None
        self.log_sms(subscriber, body, phone_number)
        return HttpResponse('<Response></Response>', mimetype='text/xml')


class TigerSubscriptionView(SubscriptionView):
    def get_host(self):
        return self.request.site.tiger_domain() 

    def get_sms_settings(self):
        return self.request.site.sms

    def matches_condition(self, keyword):
        return keyword in self.settings.keywords

    def log_sms(self, subscriber, body, phone_number):
        SMS.objects.create(
            settings=self.settings, 
            subscriber=subscriber, 
            destination=SMS.DIRECTION_INBOUND,
            body=body,
            phone_number=phone_number,
            conversation=body != 'out' and body not in self.settings.keywords
        )
