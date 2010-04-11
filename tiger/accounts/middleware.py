from django.conf import settings
from django.http import HttpResponseNotFound
from django.utils.cache import patch_vary_headers

from tiger.accounts.models import Site
from tiger.utils.site import RequestSite


class DomainDetectionMiddleware(object):
    def process_request(self, request):
        """Gets the domain from the request headers and adds a ``site`` 
        attribute to the ``Request`` object.
        """
        site = RequestSite(request)
        # Takeout Tiger itself has different URL patterns
        if site.domain == 'www.takeouttiger.com':
            request.urlconf = settings.TIGER_URLCONF
            return None
        site_obj = site.get_site_object()
        if site_obj is None:
            return HttpResponseNotFound()
        request.site = site_obj

    def process_response(self, request, response):
        patch_vary_headers(response, ('Host',))
        return response
