from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden

import twilio

from tiger.sms.models import SmsSubscriber, SMS


class SubscriptionView(object):
    def absolute_url(self, request):
        return ''.join([
            'http%s://' % ('s' if request.META['HTTP_X_FORWARDED_PORT'] == '443' else ''),
            self.get_host(request),
            request.path
        ])

    def get_host(self, request):
        raise NotImplementedError

    def get_sms_settings(self, request):
        raise NotImplementedError 

    def matches_condition(self, request, keyword):
        raise NotImplementedError 

    def log_sms(self, request, subscriber, body, phone_number):
        raise NotImplementedError

    def __call__(self, request, *args, **kwargs):
        utils = twilio.Utils(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_ACCOUNT_TOKEN)
        if not utils.validateRequest(self.absolute_url(request), request.POST, request.META['HTTP_X_TWILIO_SIGNATURE']):
            return HttpResponseForbidden()
        sms_settings = self.get_sms_settings(request)
        body = request.POST.get('Body', '')
        normalized_body = body.strip().lower()
        phone_number = request.POST.get('From')
        try:
            subscriber = SmsSubscriber.objects.get(settings=sms_settings, phone_number=phone_number)
        except SmsSubscriber.DoesNotExist:
            if self.matches_condition(request, normalized_body):
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
        self.log_sms(request, subscriber, body, phone_number)
        return HttpResponse('<Response></Response>', mimetype='text/xml')


class TigerSubscriptionView(SubscriptionView):
    def get_host(self, request):
        return '%s.takeouttiger.com' % request.site.subdomain

    def get_sms_settings(self, request):
        return request.site.sms

    def matches_condition(self, request, keyword):
        return keyword in self.get_sms_settings(request).keywords

    def log_sms(self, request, subscriber, body, phone_number):
        settings = self.get_sms_settings(request)
        SMS.objects.create(
            settings=settings, 
            subscriber=subscriber, 
            destination=SMS.DIRECTION_INBOUND,
            body=body,
            phone_number=phone_number,
            conversation=body.strip().lower() != 'out' and body.strip().lower() not in settings.keywords
        )
