from django.http import HttpResponseNotFound

from tiger.accounts.models import Site

class DomainDetectionMiddleware(object):
    def process_request(self, request):
        """Gets the domain from the request headers and adds a ``site`` attribute
        to the ``Request`` object.
        """
        host = request.META['HTTP_HOST']
        # nginx will redirect all "www-less" requests to being prefixed with "www",
        # so we can confidently assume that the subdomain is either a customer
        # site domain or "www"
        subdomain, domain = host.split('.', 1)
        if domain == 'takeouttiger.com':
            domain = subdomain
        else:
            domain, tld = domain.split('.')
        try:
            site = Site.objects.get(domain=domain)
        except Site.DoesNotExist:
            return HttpResponseNotFound()
        request.site = site
        print site
