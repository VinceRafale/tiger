from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponseNotFound, HttpResponsePermanentRedirect, HttpResponseRedirect, get_host
from django.utils.cache import patch_vary_headers

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
            return HttpResponseRedirect('http://www.takeouttiger.com')
        request.site = site_obj

    def process_response(self, request, response):
        patch_vary_headers(response, ('Host',))
        return response


class LocationMiddleware(object):
    def process_request(self, request):
        """Sets user-selected location as attribute on request object.
        """
        setattr(request, 'location', self.get_location(request))

    def get_location(self, request):
        location = cache.get('location')
        if location is None:
            try:
                location = request.site.location_set.all()[0]
            except:
                pass
        return location
