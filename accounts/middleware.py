from django.conf import settings
from django.http import HttpResponseNotFound
from django.utils.cache import patch_vary_headers

from tiger.accounts.models import Site

class DomainDetectionMiddleware(object):
    def process_request(self, request):
        """Gets the domain from the request headers and adds a ``site`` 
        attribute to the ``Request`` object.
        """
        components = self.get_domain_components(request)
        try:
            site = self.get_site_from_domain(*components)
        except Site.DoesNotExist:
            subdomain = components[0]
            if subdomain == 'www':
                # Takeout Tiger itself has different URL patterns
                request.urlconf = settings.TIGER_URLCONF
                return None
            return HttpResponseNotFound()
        request.site = site

    def process_response(self, request, response):
        patch_vary_headers(response, ('Host',))
        return response

    @staticmethod
    def get_domain_components(request):
        host = request.META['HTTP_HOST']
        if ':' in host:
            host = host[:host.find(':')]
        # nginx will redirect all "www-less" requests to being prefixed with 
        # "www", so we can confidently assume that the subdomain is either a 
        # customer site domain or "www"
        return host.split('.')

    @staticmethod
    def get_site_from_domain(subdomain=None, domain=None, tld=None):
        if domain == 'takeouttiger': 
            if subdomain == 'www':
                raise Site.DoesNotExist
            domain = subdomain
        return Site.objects.get(domain=domain)

    @staticmethod
    def get_site(request):
        components = DomainDetectionMiddleware.get_domain_components(request)
        try: 
            return DomainDetectionMiddleware.get_site_from_domain(*components)
        except Site.DoesNotExist:
            return None
