from mock import Mock, patch
import faker
from should_dsl import should, should_not

from tiger.accounts.models import Site
from tiger.sales.models import Plan
from tiger.sms.models import SmsSettings, SmsSubscriber, SMS
from tiger.sms.sender import Sender
from tiger.utils.test import TestCase


class AutomatedResponseTestCase(TestCase):
    fixtures = ['plans.json']
    poseur_fixtures = 'tiger.fixtures'

    def setUp(self):
        self.site = Site.objects.all()[0]
        self.site.plan = Plan.objects.get(name='no caps')
        self.site.save()
        self.settings = self.site.sms 
        self.settings.sms_number = '000-000-0000'
        self.settings.send_intro = True
        self.settings.intro_sms = 'Free coffee!'
        self.settings.save()

    def get_mock_sender(self):
        sender = Sender(self.site, self.settings.intro_sms) 
        sender.get_sms_response = Mock(return_value={})
        return sender

    @patch.object(SmsSubscriber, 'sender')
    def test_signup_triggers_intro_sms_if_enabled(self, mock_method):
        "signup triggers intro sms if enabled"
        self.settings.send_intro = True
        self.settings.save()
        number = faker.phone_number.phone_number()[:20]
        mock_method.return_value = self.get_mock_sender()
        s = SmsSubscriber.objects.create(settings=self.settings, phone_number=number)
        self.assertTrue(s.sender.called)
        sms = SMS.objects.get(subscriber=s)
        sms.body |should| start_with(self.settings.intro_sms)
        sms.body |should| end_with(' Reply "out" to quit')

    @patch.object(SmsSubscriber, 'sender')
    def test_signup_does_not_trigger_intro_sms_if_disabled(self, mock_method):
        "signup does not trigger intro sms if disabled"
        self.settings.send_intro = False
        self.settings.save()
        number = faker.phone_number.phone_number()[:20]
        mock_method.return_value = self.get_mock_sender()
        s = SmsSubscriber.objects.create(settings=self.settings, phone_number=number)
        s = SmsSubscriber.objects.create(settings=self.settings, phone_number=number)
        self.assertFalse(s.sender.called)
        self.assertRaises(SMS.DoesNotExist, SMS.objects.get, subscriber=s, body=self.settings.intro_sms)
