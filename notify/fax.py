import urllib
import urllib2

from lxml.etree import parse

from django.template.loader import render_to_string

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

    def send(self, contacts, content, content_type='HTML', **kwargs):
        b64_content = content.encode('base64')
        params = {
            'Username': self.username,
            'Password': self.password,
            'FaxNumbers': ';'.join(contact.fax_number for contact in contacts),
            'Contacts': ';'.join(contact.user.get_full_name() for contact in contacts),
            'FilesData': b64_content,
            'FileTypes': content_type,
            'FileSizes': len(b64_content),
            'Postpone': '2000-01-01',
            'RetriesToPerform': 2,
            'PageHeader': 'N',
            'IsHighResolution': 'False',
            'IsFineRendering': 'False',
        }
        try:
            response = urllib2.urlopen(SEND_FAX_ENDPOINT, urllib.urlencode(params))
        except urllib2.HTTPError:
            raise FaxServiceError
        doc = parse(response).getroot()
        transaction_id = doc.text
        if len(contacts) > 1:
            is_parent = True
        else:
            is_parent = False
        faxes = self.query_by_transaction_id(transaction_id, is_parent)
        #TODO: get sum of pages
        return Fax.objects.create(site=self.site, page_count=page_count)

    def query_by_transaction_id(self, transaction_id, is_parent):
        #TODO: use suds to query
        pass
