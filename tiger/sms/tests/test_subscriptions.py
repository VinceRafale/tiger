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
from tiger.sms.models import SmsSubscriber
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

def test_non_keyword_does_not_subscribe():
    data = get_data_for_request(faker.lorem.sentence())
    site = Site.objects.all()[0]
    twilio_header = get_twilio_header(site.tiger_domain() + '/sms/respond-to-sms/', data)
    response = client.post('/sms/respond-to-sms/', data, 
        HTTP_X_TWILIO_SIGNATURE=twilio_header)
    subscriber = SmsSubscriber.objects.get(phone_number=data['From'])
    assert_false(subscriber.is_active)

def test_non_keyword_does_not_unsubscribe():
    data = get_data_for_request(faker.lorem.sentence())
    site = Site.objects.all()[0]
    SmsSubscriber.objects.create(phone_number=data['From'], settings=site.sms)
    twilio_header = get_twilio_header(site.tiger_domain() + '/sms/respond-to-sms/', data)
    response = client.post('/sms/respond-to-sms/', data, 
        HTTP_X_TWILIO_SIGNATURE=twilio_header)
    assert SmsSubscriber.objects.get(phone_number=data['From'])
