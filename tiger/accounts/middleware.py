from django.conf import settings
from django.http import HttpResponseNotFound, HttpResponsePermanentRedirect, HttpResponseRedirect, get_host
from django.utils.cache import patch_vary_headers

from tiger.utils.site import RequestSite


SSL = 'SSL'


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


class SSLRedirectMiddleware(object):
    def process_view(self, request, view_func, view_args, view_kwargs):
        if SSL in view_kwargs:
            secure = view_kwargs[SSL]
            del view_kwargs[SSL]
        else:
            secure = False

        if not secure == self._is_secure(request):
            return self._redirect(request, secure)

    def _is_secure(self, request):
        if request.META.has_key('HTTP_X_FORWARDED_PORT') and request.META['HTTP_X_FORWARDED_PORT'] == '443':
            return True

        #Handle the Webfaction case until this gets resolved in the request.is_secure()
        if 'HTTP_X_FORWARDED_SSL' in request.META:
            return request.META['HTTP_X_FORWARDED_SSL'] == 'on'

        return False

    def _redirect(self, request, secure):
        protocol = secure and "https" or "http"
        newurl = "%s://%s%s" % (protocol,get_host(request),request.get_full_path())
        if settings.DEBUG and request.method == 'POST':
            raise RuntimeError, \
        """Django can't perform a SSL redirect while maintaining POST data.
           Please structure your views so that redirects only occur during GETs."""

        return HttpResponsePermanentRedirect(newurl)
