import re
import urllib
import urllib2

from lxml.etree import parse
from suds.client import Client

from django.conf import settings
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from tiger.notify.models import Fax

SEND_FAX_ENDPOINT = 'http://ws.interfax.net/dfs.asmx/SendfaxEx_2'
QUERY_FAX_ENDPOINT = 'http://ws.interfax.net/dfs.asmx'


class FaxServiceError(Exception):
    pass


class FaxMachine(object):
    def __init__(self, site, username=settings.INTERFAX_USERNAME, 
                 password=settings.INTERFAX_PASSWORD):
        self.site = site
        self.username = username
        self.password = password

    def send(self, contacts, content, content_type='PDF', **kwargs):
        b64_content = content.encode('base64')
        params = {
            'Username': self.username,
            'Password': self.password,
            'FaxNumbers': ';'.join('+1 (%s) %s %s' % tuple(contact.fax.split('-')) for contact in contacts),
            'Contacts': ';'.join(contact.user.get_full_name() for contact in contacts),
            'FilesData': b64_content,
            'FileTypes': content_type,
            'FileSizes': len(content),
            'Postpone': '2000-01-01',
            'RetriesToPerform': 2,
            'PageHeader': 'N',
            'IsHighResolution': False,
            'IsFineRendering': False
        }
        c = Client('https://ws.interfax.net/dfs.asmx?WSDL')
        try:
            result = c.service.SendfaxEx_2(**params)
        except Exception, e:
            raise FaxServiceError()
        transaction_id = result
        if transaction_id < 0:
            #TODO: log negative values
            raise FaxServiceError()
        if len(contacts) > 1:
            is_batch = True
        else:
            is_batch = False
        return Fax.objects.create(transaction=transaction_id, batch=is_batch, site=self.site)
