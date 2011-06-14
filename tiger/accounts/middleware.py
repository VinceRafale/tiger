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
        from tiger.accounts.models import Site
        request.site = Site.objects.get(subdomain='casadenana')

    def process_response(self, request, response):
        patch_vary_headers(response, ('Host',))
        return response


class LocationMiddleware(object):
    def process_request(self, request):
        """Sets user-selected location as attribute on request object.
        """
        setattr(request, 'location', self.get_location(request))

    def get_location(self, request):
        if request.path.startswith('/dashboard'):
            return self._dashboard_location(request)
        return self._homepage_location(request)

    def _dashboard_location(self, request):
        return request.session.get('dashboard-location') or request.site.location_set.all()[0]

    def _homepage_location(self, request):
        if request.site.location_set.count() == 1:
            return request.site.location_set.all()[0]
        return request.session.get('location')
