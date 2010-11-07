from tiger.track.models import Hit

class TrackingMiddleware(object):
    def process_response(self, request, response):
        if hasattr(request, 'site') and not request.path.startswith('/dashboard'):
            # If it's their first request, they won't have a cookie set yet,
            # and it'll be returned in the response, so we have to check the 
            # response and the request.
            cookies = request.COOKIES
            cookies_from_request = True
            if not len(cookies):
                cookies = response.cookies
                cookies_from_request = False
            cookie_name, session_key = [
                (k, v) for k, v in cookies.items()
                if k.startswith('takeouttiger')
            ][0]
            if not cookies_from_request:
                session_key = session_key.value
            Hit.objects.record_hit(
                request.site, 
                request.location, 
                session_key, 
                response.status_code, 
                request)
        return response    
