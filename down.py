from urlparse import urlsplit

def app(environ, start_response):
    site = urlsplit(environ['HTTP_HOST']).hostname.lower()
    try:
        data = open('sites/%s.html' % site).read()
    except IOError:
        start_response("302 Redirect", [
            ("Location", "http://www.takeouttiger.com")
        ])
        return []
    start_response("200 OK", [
        ("Content-Type", "text/html"),
        ("Content-Length", str(len(data)))
    ])
    return [data]
