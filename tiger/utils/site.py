import re

from django.contrib.sites.models import RequestSite as BaseRequestSite

from tiger.accounts.models import Site


subdomain_re = re.compile(r'([\w-]+)\.takeouttiger\.com')

class RequestSite(BaseRequestSite):
    def __init__(self, request):
        super(RequestSite, self).__init__(request)
        if ':' in self.domain:
            self.domain, self.port = self.domain.split(':')

    def get_site_object(self):
        # check if it's a takeouttiger.com subdomain
        m = subdomain_re.match(self.domain)
        if m:
            subdomain = m.group(1)
            try:
                return Site.objects.get(subdomain__iexact=subdomain)
            except Site.DoesNotExist:
                return None
        # if not, check for custom domains
        try:
            domain = Site.objects.get(domain__iexact=self.domain)
        except Site.DoesNotExist:
            return None
        return domain
