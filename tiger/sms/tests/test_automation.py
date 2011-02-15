import unittest

from mock import Mock, patch
import faker

from tiger.sms.models import SmsSettings, SmsSubscriber, SMS


class AutomatedResponseTestCase(unittest.TestCase):
    def setUp(self):
        self.settings = SmsSettings.objects.create(
            sms_number='000-000-0000',
            send_intro=True,
            intro_sms='Free coffee!'
        )

    def test_signup_triggers_intro_sms_if_enabled(self):
        "signup triggers intro sms if enabled"
        self.settings.send_intro = True
        self.settings.save()
        number = faker.phone_number.phone_number()[:20]
        with patch.object(SmsSubscriber, 'get_sms_response') as mock_method:
            mock_method.return_value = {}
            s = SmsSubscriber.objects.create(settings=self.settings, phone_number=number)
            self.assertTrue(s.get_sms_response.called)
            assert SMS.objects.get(subscriber=s, body=self.settings.intro_sms)

    def test_signup_does_not_trigger_intro_sms_if_disabled(self):
        "signup does not trigger intro sms if disabled"
        self.settings.send_intro = False
        self.settings.save()
        number = faker.phone_number.phone_number()[:20]
        with patch.object(SmsSubscriber, 'get_sms_response') as mock_method:
            mock_method.return_value = {}
            s = SmsSubscriber.objects.create(settings=self.settings, phone_number=number)
            self.assertFalse(s.get_sms_response.called)
            self.assertRaises(SMS.DoesNotExist, SMS.objects.get, subscriber=s, body=self.settings.intro_sms)
