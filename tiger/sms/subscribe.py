import re

from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden

import twilio

from tiger.sales.models import Account
from tiger.sms.models import SmsSubscriber, SMS


class SubscriptionView(object):
    def absolute_url(self, request, *args, **kwargs):
        return ''.join([
            'http%s://' % ('s' if request.META['HTTP_X_FORWARDED_PORT'] == '443' else ''),
            self.get_host(request),
            request.path
        ])

    def get_host(self, request, *args, **kwargs):
        raise NotImplementedError

    def get_sms_settings(self, request, *args, **kwargs):
        raise NotImplementedError 

    def matches_condition(self, request, keyword, *args, **kwargs):
        raise NotImplementedError 

    def log_sms(self, request, subscriber, body, phone_number, *args, **kwargs):
        settings = self.get_sms_settings(request, *args, **kwargs)
        SMS.objects.create(
            settings=settings, 
            subscriber=subscriber, 
            destination=SMS.DIRECTION_INBOUND,
            body=body,
            phone_number=phone_number,
            conversation=body.strip().lower() != 'out' and not self.matches_condition(request, body) 
        )

    def __call__(self, request, *args, **kwargs):
        utils = twilio.Utils(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_ACCOUNT_TOKEN)
        if not utils.validateRequest(self.absolute_url(request, *args, **kwargs), request.POST, request.META['HTTP_X_TWILIO_SIGNATURE']):
            return HttpResponseForbidden()
        sms_settings = self.get_sms_settings(request, *args, **kwargs)
        body = request.POST.get('Body', '')
        phone_number = request.POST.get('From')
        try:
            subscriber = SmsSubscriber.objects.get(settings=sms_settings, phone_number=phone_number)
        except SmsSubscriber.DoesNotExist:
            normalized_body = self.matches_condition(request, body, *args, **kwargs)
            if normalized_body:
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
        self.log_sms(request, subscriber, body, phone_number, *args, **kwargs)
        return HttpResponse('<Response></Response>', mimetype='text/xml')


class TigerSubscriptionView(SubscriptionView):
    def get_host(self, request, *args, **kwargs):
        return '%s.takeouttiger.com' % request.site.subdomain

    def get_sms_settings(self, request, *args, **kwargs):
        return request.site.sms

    def matches_condition(self, request, keyword, *args, **kwargs):
        normalize = lambda k: k.lower().strip()
        normal = normalize(keyword)
        if normal in [normalize(k) for k in self.get_sms_settings(request).keywords]:
            return normal
        return False


class ResellerSubscriptionView(SubscriptionView):
    ZIP_CODE_RE = re.compile(r'(\d{5})(?:-\d{4})?')

    def get_host(self, request, *args, **kwargs):
        return 'www.takeouttiger.com'

    def get_sms_settings(self, request, reseller_id, *args, **kwargs):
        return Account.objects.get(id=reseller_id)

    def matches_condition(self, request, keyword, *args, **kwargs):
        m = ZIP_CODE_RE.match(keyword.strip())
        if m:
            return m.group(1)
        return False
