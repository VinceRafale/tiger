from django.http import HttpResponseRedirect

class DashboardSecurityMiddleware(object):
    def process_request(self, request):
        if not request.path.startswith('/dashboard/'):
            return None
        host = request.META['HTTP_HOST']
        if 'takeouttiger.com' not in host:
            return HttpResponseRedirect(request.site.tiger_domain() + request.path)
        return None
