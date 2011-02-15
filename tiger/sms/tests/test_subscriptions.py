import base64
from hashlib import sha1
import hmac

from django.core.management import call_command
from django.conf import settings
from django.db import transaction, IntegrityError
from django.test.client import Client

import faker
from poseur.fixtures import load_fixtures

from tiger.accounts.models import Site
from tiger.sms.models import SmsSubscriber, SMS
from tiger.utils.test import TestCase

from nose.tools import *

client = Client(HTTP_HOST='foo.takeouttiger.com')

def setupModule():
    try:
        load_fixtures('tiger.fixtures')
    except IntegrityError:
        transaction.rollback()
    site = Site.objects.all()[0]
    sms = site.sms
    sms.sms_number = faker.phone_number.phone_number()[:20]
    sms.send_intro = False
    sms.save()

def teardownModule():
    call_command('flush', verbosity=0, interactive=False, database='default')

def get_keyword_variants(keyword):
    return [
        keyword,
        keyword.upper(),
        ' %s ' % keyword,
        ' %s ' % keyword.upper()
    ]

def get_data_for_request(body):
    return {
        'Body': body,
        'From': faker.phone_number.phone_number()[:20],
        'FromCity': faker.address.city(),
        'FromState': faker.address.us_state_abbr(),
        'FromZip': faker.address.zip_code()[:10]
    }

def get_twilio_header(uri, postVars):
    """Taken from the Twilio Python client."""
    s = uri
    if len(postVars) > 0:
        for k, v in sorted(postVars.items()):
            s += k + v
    return base64.encodestring(hmac.new(settings.TWILIO_ACCOUNT_TOKEN, s, sha1).digest()).strip()

def test_subscribe_keywords_subscribe():
    keyword = 'in'
    for kw in get_keyword_variants(keyword):
        yield check_subscribe, kw

def check_subscribe(keyword):
    data = get_data_for_request(keyword)
    site = Site.objects.all()[0]
    twilio_header = get_twilio_header(site.tiger_domain() + '/sms/respond-to-sms/', data)
    response = client.post('/sms/respond-to-sms/', data, 
        HTTP_X_TWILIO_SIGNATURE=twilio_header)
    print response.status_code
    assert SmsSubscriber.objects.get(phone_number=data['From'])

def test_unsubscribe_keywords_unsubscribe():
    keyword = 'out'
    for kw in get_keyword_variants(keyword):
        yield check_unsubscribe, kw

def check_unsubscribe(keyword):
    data = get_data_for_request(keyword)
    site = Site.objects.all()[0]
    SmsSubscriber.objects.create(phone_number=data['From'], settings=site.sms)
    twilio_header = get_twilio_header(site.tiger_domain() + '/sms/respond-to-sms/', data)
    response = client.post('/sms/respond-to-sms/', data, 
        HTTP_X_TWILIO_SIGNATURE=twilio_header)
    subscriber = SmsSubscriber.objects.get(phone_number=data['From'])
    assert_false(subscriber.is_active)


class ConversationalSMSTestCase(TestCase):
    poseur_fixtures = 'tiger.fixtures'

    def setUp(self):
        self.site = Site.objects.all()[0]
        sms = self.site.sms
        sms.sms_number = faker.phone_number.phone_number()[:20]
        sms.send_intro = False
        sms.save()
        self.data = get_data_for_request(faker.lorem.sentence())
        self.twilio_header = get_twilio_header(self.site.tiger_domain() + '/sms/respond-to-sms/', self.data)

    def get_response(self):
        return client.post('/sms/respond-to-sms/', self.data, 
            HTTP_X_TWILIO_SIGNATURE=self.twilio_header)

    def test_non_keyword_does_not_subscribe(self):
        response = self.get_response()
        self.assertRaises(SmsSubscriber.DoesNotExist, SmsSubscriber.objects.get, phone_number=self.data['From'])

    def test_non_keyword_sms_is_saved_as_conversation(self):
        response = self.get_response()
        latest_sms = SMS.objects.order_by('-timestamp')[0]
        assert_true(latest_sms.conversation)

    def test_non_keyword_phone_number_is_saved(self):
        response = self.get_response()
        latest_sms = SMS.objects.order_by('-timestamp')[0]
        self.assertEquals(latest_sms.phone_number, self.data['From'])

    def test_non_keyword_does_not_unsubscribe(self):
        SmsSubscriber.objects.create(phone_number=self.data['From'], settings=self.site.sms)
        response = self.get_response()
        assert SmsSubscriber.objects.get(phone_number=self.data['From'])
