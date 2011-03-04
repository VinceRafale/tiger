from datetime import datetime
from django.conf import settings
from django.utils import simplejson as json
import twilio

class Sender(object):
    def __init__(self, site, body, sms_number=None, campaign=None, reseller=False):
        self.site = site
        self.settings = site.sms
        self.body = body[:140] + ' Reply "out" to quit'
        if sms_number is None:
            sms_number = self.settings.sms_number
        self.sms_number = sms_number
        self.campaign = campaign
        self.is_reseller = reseller

    def add_recipients(self, *recipients):
        from tiger.sms.models import SMS
        if not self.is_reseller:
            plan = self.site.plan
            this_month = datetime.now().replace(day=1, hour=0, minute=0)
            smses_this_month = SMS.objects.filter(
                settings=self.settings, timestamp__gte=this_month).count()
            resulting_sms_count = smses_this_month + len(recipients)
            plan.assert_sms_cap_not_exceeded(resulting_sms_count)
        if isinstance(recipients[0], basestring):
            self.recipients = [(None, number) for number in recipients]
        else:
            self.recipients = [(recipient, recipient.phone_number) for recipient in recipients]

    def send_message(self):
        for subscriber, number in self.recipients:
            data = self.get_sms_response(number)
            self.record_sms(self.settings, self.campaign, subscriber, self.body, number)
            if self.campaign:
                self.campaign.sent_count += 1
                self.campaign.save()

    def get_sms_response(self, phone_number): 
        account = twilio.Account(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_ACCOUNT_TOKEN)
        response = account.request('/2010-04-01/Accounts/%s/SMS/Messages.json' % settings.TWILIO_ACCOUNT_SID, 'POST', dict(From=self.sms_number, To=phone_number, Body=self.body))
        return json.loads(response)

    def record_sms(self, settings, campaign, subscriber, body, phone_number):
        from tiger.sms.models import SMS
        SMS.objects.create(
            settings=settings,
            campaign=campaign,
            subscriber=subscriber,
            body=body,
            destination=SMS.DIRECTION_OUTBOUND,
            phone_number=phone_number,
            conversation=False if campaign else True
        )
