
mobile_uas = [
    'w3c ','acs-','alav','alca','amoi','audi','avan','benq','bird','blac',
    'blaz','brew','cell','cldc','cmd-','dang','doco','eric','hipt','inno',
    'ipaq','java','jigs','kddi','keji','leno','lg-c','lg-d','lg-g','lge-',
    'maui','maxo','midp','mits','mmef','mobi','mot-','moto','mwbp','nec-',
    'newt','noki','palm','pana','pant','phil','play','port','prox','qwap',
    'sage','sams','sany','sch-','sec-','send','seri','sgh-','shar','sie-',
    'siem','smal','smar','sony','sph-','symb','t-mo','teli','tim-','tosh',
    'tsm-','upg1','upsi','vk-v','voda','wap-','wapa','wapi','wapp','wapr',
    'webc','winw','winw','xda','xda-'
    ]
 
mobile_ua_hints=['SymbianOS', 'Opera Mini', 'iPhone', 'Android', 'Opera Mobi', 'webOS']


def is_mobile_browser(request):
    full_ua = request.META.get('HTTP_USER_AGENT', '')
    ua = full_ua.lower()[0:4]
 
    if ua in mobile_uas:
        return True

    for hint in mobile_ua_hints:
        if full_ua.find(hint) >= 0:
            return True
 
    return False

class MobileTiger(object):
    """Middleware to detect if a useragent is mobile and set a session accordingly"""
    def process_request(self, request):
        state = request.session.get('state')
        if state is None:
            mobile = is_mobile_browser(request)
            if mobile:
                request.session['state'] = 'mobile'
            else:
                request.session['state'] = 'full'
        else:
            if state == 'mobile':
                # do stuff for mobile here
            else:
                # do stuff for not mobile here
        request.is_mobile = mobile

