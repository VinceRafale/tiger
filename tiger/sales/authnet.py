import urllib2

from lxml import etree
from lxml import objectify

from django.conf import settings
from tiger.sales.exceptions import PaymentGatewayError


CREDIT_CARD_ERROR_MESSAGE = 'Unable to process your credit card information.'
AUTH_NET_ENDPOINT = 'https://api.authorize.net/xml/v1/request.api'


class Cim(object):
    """Mixin class for adding CIM-specific methods to other classes.
    """
    login = settings.AUTHORIZENET_API_LOGIN
    api_key = settings.AUTHORIZENET_API_KEY

    def get_xml(self, method):
        """Creates incomplete XML document for ``method`` with authentication information
        in place.
        """
        root = etree.Element(method, xmlns='AnetApi/xml/v1/schema/AnetApiSchema.xsd')
        auth = etree.SubElement(root, 'merchantAuthentication')
        login = etree.SubElement(auth, 'name')
        login.text = self.login
        key = etree.SubElement(auth, 'transactionKey')
        key.text = self.api_key
        return root

    def fetch(self, xml):
        request = urllib2.Request(AUTH_NET_ENDPOINT, etree.tostring(xml), {'Content-Type': 'text/xml'})
        response = urllib2.urlopen(request)
        return objectify.parse(response).getroot()

    def create_cim_profile(self, customer_id, card_number, expiration_date, first_name, last_name):
        xml = self.get_xml('createCustomerProfileRequest') 
        profile = etree.SubElement(xml, 'profile')
        cust = etree.SubElement(profile, 'merchantCustomerId')
        cust.text = str(customer_id)
        payment_profiles = etree.SubElement(profile, 'paymentProfiles')
        billto = etree.SubElement(payment_profiles, 'billTo')
        first = etree.SubElement(billto, 'firstName')
        first.text = first_name
        last = etree.SubElement(billto, 'lastName')
        last.text = last_name
        payment = etree.SubElement(payment_profiles, 'payment')
        card = etree.SubElement(payment, 'creditCard')
        card_num = etree.SubElement(card, 'cardNumber')
        card_num.text = str(card_number)
        exp_date = etree.SubElement(card, 'expirationDate')
        exp_date.text = expiration_date
        results = self.fetch(xml)
        success = results.messages.resultCode == u'Ok'
        if not success:
            raise PaymentGatewayError
        return results.customerProfileId, results.customerPaymentProfileIdList.numericString[0]

    def create_profile_transaction(self, amount, customer_profile_id, customer_payment_profile_id, invoice, profile_type=u'AUTH_CAPTURE'):
        xml = self.get_xml('createCustomerProfileTransactionRequest') 
        transaction = etree.SubElement(xml, 'transaction')
        auth_capture = etree.SubElement(transaction, 'profileTransAuthCapture')
        amt = etree.SubElement(auth_capture, 'amount')
        amt.text = str(amount)
        customer_profile = etree.SubElement(auth_capture, 'customerProfileId')
        customer_profile.text = str(customer_profile_id)
        customer_payment_profile = etree.SubElement(auth_capture, 'customerPaymentProfileId')
        customer_payment_profile.text = str(customer_payment_profile_id)
        order = etree.SubElement(auth_capture, 'order')
        invoice_number = etree.SubElement(order, 'invoiceNumber')
        invoice_number.text = invoice.invoiceno
        results = self.fetch(xml)
        success = results.messages.resultCode == u'Ok'
        if not success:
            raise PaymentGatewayError
        return True

