from suds.client import Client

from django.conf import settings

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

    def send(self, fax_numbers, content, content_type='PDF', names=None, **kwargs):
        b64_content = content.encode('base64')
        if not isinstance(fax_numbers, list):
            fax_numbers = [fax_numbers]
        if names is None:
            names = [self.site.name]
        params = {
            'Username': self.username,
            'Password': self.password,
            'FaxNumbers': ';'.join('+1 (%s) %s %s' % tuple(num.split('-')) for num in fax_numbers),
            'Contacts': ';'.join(names), 
            'FilesData': b64_content,
            'FileTypes': content_type,
            'FileSizes': len(content),
            'Postpone': '2000-01-01',
            'RetriesToPerform': 2,
            'PageHeader': 'N',
            'IsHighResolution': False,
            'IsFineRendering': False
        }
        params.update(kwargs)
        try:
            c = Client('https://ws.interfax.net/dfs.asmx?WSDL', cache=None)
        except:
            raise FaxServiceError()
        result = c.service.SendfaxEx_2(**params)
        transaction_id = result
        if transaction_id < 0:
            #TODO: log negative values
            raise FaxServiceError()
        return Fax.objects.create(parent_transaction=transaction_id, 
            transaction=transaction_id, site=self.site)
