from decimal import Decimal
import datetime
from poseur.fixtures import FakeModel
from django.contrib.sessions.models import Session
from tiger.core.models import Coupon
import faker

TEST_PAYPAL_TRANSACTION = {
     'address_city': u'',
     'address_country': u'',
     'address_country_code': u'',
     'address_name': u'',
     'address_state': u'',
     'address_status': u'',
     'address_street': u'',
     'address_zip': u'',
     'auction_buyer_id': u'',
     'auth_exp': u'',
     'auth_id': u'',
     'auth_status': u'',
     'business': u'onlineorders@spinellapastabar.com',
     'case_id': u'',
     'case_type': u'',
     'charset': u'windows-1252',
     'contact_phone': u'',
     'created_at': datetime.datetime(2010, 8, 13, 21, 53, 28, 170026),
     'currency_code': u'',
     'custom': u'',
     'first_name': u'mirko',
     'flag_code': u'',
     'flag_info': u'Invalid receiver_email. (onlineorders@spinellapastabar.com)',
     'handling_amount': Decimal('0.00'),
     'invoice': u'46',
     'ipaddress': '127.0.0.1',
     'item_name': u'Your order at Spinella Pasta Bar',
     'item_number': u'',
     'last_name': u'spinella',
     'mc_currency': u'USD',
     'mc_fee': Decimal('0.10'),
     'mc_gross': Decimal('1.00'),
     'memo': u'',
     'notify_version': Decimal('3.00'),
     'option_name1': u'',
     'option_name2': u'',
     'parent_txn_id': u'',
     'password': u'',
     'payer_business_name': u'',
     'payer_email': u'mirkospinella@gmail.com',
     'payer_id': u'4BQP5CYGLV2TG',
     'payer_status': u'unverified',
     'payment_cycle': u'',
     'payment_date': datetime.datetime(2010, 8, 13, 18, 53, 25),
     'payment_gross': Decimal('1.00'),
     'payment_status': u'Completed',
     'payment_type': u'instant',
     'pending_reason': u'',
     'period1': u'',
     'period2': u'',
     'period3': u'',
     'period_type': u'',
     'product_name': u'',
     'product_type': u'',
     'profile_status': u'',
     'protection_eligibility': u'Ineligible',
     'quantity': 1,
     'query': u'protection_eligibility=Ineligible&last_name=spinella&txn_id=35Y849735F4659902&receiver_email=onlineorders%40spinellapastabar.com&payment_status=Completed&payment_gross=1.00&tax=0.00&residence_country=US&invoice=46&payer_status=unverified&txn_type=web_accept&handling_amount=0.00&payment_date=18%3A53%3A25+Aug+13%2C+2010+PDT&first_name=mirko&item_name=Your+order+at+Spinella+Pasta+Bar&charset=windows-1252&custom=&notify_version=3.0&transaction_subject=Your+order+at+Spinella+Pasta+Bar&item_number=&receiver_id=CFUXU3GBJQSWA&business=onlineorders%40spinellapastabar.com&payer_id=4BQP5CYGLV2TG&verify_sign=AzEP17uSCKIGqIhT5rZpY.vz94soASf4zX6Cfg-l79n2EDV.SA-GpnhJ&payment_fee=0.10&receipt_id=3846-7849-5474-7870&mc_fee=0.10&mc_currency=USD&shipping=0.00&payer_email=mirkospinella%40gmail.com&payment_type=instant&mc_gross=1.00&quantity=1',
     'reason_code': u'',
     'reattempt': u'',
     'receipt_id': u'3846-7849-5474-7870',
     'receiver_email': u'onlineorders@spinellapastabar.com',
     'receiver_id': u'CFUXU3GBJQSWA',
     'recurring': u'',
     'recurring_payment_id': u'',
     'residence_country': u'US',
     'response': u'VERIFIED',
     'rp_invoice_id': u'',
     'settle_currency': u'',
     'shipping': Decimal('0.00'),
     'shipping_method': u'',
     'subscr_id': u'',
     'tax': Decimal('0.00'),
     'test_ipn': False,
     'transaction_entity': u'',
     'transaction_subject': u'Your order at Spinella Pasta Bar',
     'txn_id': u'35Y849735F4659902',
     'txn_type': u'web_accept',
     'updated_at': datetime.datetime(2010, 8, 13, 21, 53, 28, 180026),
     'username': u'',
     'verify_sign': u'AzEP17uSCKIGqIhT5rZpY.vz94soASf4zX6Cfg-l79n2EDV.SA-GpnhJ'
}

class FakeSession(FakeModel):
    session_key = 'test_tiger'
    session_data = Session.objects.encode({})
    expire_date = datetime.datetime.now() + datetime.timedelta(days=7)

    class Meta:
        model = Session

class FakeCoupon(FakeModel):
    short_code = None

    class Meta:
        model = Coupon
