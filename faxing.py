import urllib2
from string import Template

from django.config import settings

USERNAME = settings.INTERFAX_USERNAME
PASSWORD = settings.INTERFAX_PASSWORD
INTERFAX_WSDL = settings.INTERFAX_WSDL

'''
Required keywords for SENDCHARFAX:
fax_number #must be +(countrycode)(areacode)(#) e.g.: +14133943333
data #a string
type #'TXT', 'HTML'
Defaults:
username = settings.USERNAME
password = settings.PASSWORD
'''
SENDCHARFAX = \
Template("Username=$username&Password=$password&FaxNumber=$fax_number&Data=$data&FileType=$type")

class Fax:
    #caching
    def __init__(self, wsdl_url=INTERFAX_WSDL, username=USERNAME, password=PASSWORD):
        self.post_to = wsdl_url
        self.__dict__ = {'username': username, 'password': password,}

    def post_to_interfax(self, template=SENDCHARFAX, **kwargs):
        '''Import the template and class Fax() then just pass the
        template along with the dictionary
        '''
        self.__dict__.update(kwargs)
        post_data = template.substitute(self.__dict__)
        return urllib2.urlopen(self.post_to, post_data)

