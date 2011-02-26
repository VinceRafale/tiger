import hashlib
import time
from datetime import datetime, timedelta
from decimal import Decimal

from django.conf import settings
from django.contrib.sessions.models import Session

from tiger.core.models import Coupon
from tiger.utils.site import RequestSite


class Cart(object):
    contents = {}

    def __init__(self, session=None, contents=None):
        self.session = session
        if contents is None:
            self.contents = session.get_decoded()
        else:
            self.contents = contents

    def __iter__(self):
        """Iterating over the cart returns a list of tuples consisting of
        the Item in the cart and the corresponding quantity.
        """
        return iter((k, v) for k, v in self.contents.items() if type(k) == int)

    def __len__(self):
        return sum(v['quantity'] for k, v in self if type(k) == int)

    def __getitem__(self, key):
        return self.contents[key]

    def __setitem__(self, key, value):
        contents = self.contents
        contents[key] = value
        self._save(contents)

    def __contains__(self, item):
        return item in self.contents

    def _save(self, contents):
        if self.session is not None:
            self.session.session_data = Session.objects.encode(contents)
            self.session.save()

    def _pop(self, key):
        contents = self.contents
        contents.pop(key, None)
        self._save(contents)

    def add(self, item, form):
        cleaned_data = form.cleaned_data
        cleaned_data.update(item.__dict__)
        if not cleaned_data.has_key('variant'):
            cleaned_data['variant'] = item.variant_set.all()[0]
        cleaned_data['sides'] = []
        for k, v in cleaned_data.items():
            if k.startswith('side_'):
                cleaned_data['sides'].append(cleaned_data.pop(k))
        cleaned_data['total'] = self.tally(cleaned_data)
        cleaned_data['name'] = '%s - %s' % (item.section.name, cleaned_data['name'])
        if item.taxable:
            tax_rate = item.site.ordersettings.tax_rate / 100
        else:
            tax_rate = Decimal('0.00')
        cleaned_data['tax'] = cleaned_data['total'] * tax_rate
        self[len(self) + 1] = cleaned_data

    def remove(self, key):
        self._pop(int(key))

    def clear(self):
        self._save({})

    def add_coupon(self, coupon):
        self['coupon'] = coupon.__dict__

    def remove_coupon(self, coupon=None):
        #TODO: remove this keyword argument entirely
        self._pop('coupon')
        
    @property
    def has_coupon(self):
        return 'coupon' in self

    def tally(self, item):
        qty = item['quantity']
        base_price = item['variant'].price
        upgrades, sides = 0, 0
        if item.has_key('upgrades'):
            upgrades = sum(upgrade.price for upgrade in item['upgrades'])
        if len(item['sides']):
            sides = sum(side.price for side in item['sides'])
        return (base_price + upgrades + sides) * qty

    def subtotal(self):
        return sum(item['total'] for k, item in self if type(k) == int)

    def taxes(self):
        return sum(item['tax'] for k, item in self if type(k) == int)

    def discount(self):
        if not self.has_coupon:
            return 0
        discount_type = self['coupon']['discount_type']
        discount_actions = {
            Coupon.DISCOUNT_DOLLARS: lambda coupon: coupon['dollars_off'],
            Coupon.DISCOUNT_PERCENT: lambda coupon: (coupon['percent_off'] / Decimal('100.00')) * self.subtotal()
        }
        return discount_actions[discount_type](self['coupon'])

    def coupon_display(self):
        if not self.has_coupon:
            return ''
        discount_type = self['coupon']['discount_type']
        discount_strings = {
            Coupon.DISCOUNT_DOLLARS: lambda: '$%.2f' % self['coupon']['dollars_off'],
            Coupon.DISCOUNT_PERCENT: lambda: '%s%%' % self['coupon']['percent_off']
        }
        return 'Coupon %s - %s off' % (self['coupon']['short_code'], discount_strings[discount_type]())

    def total(self):
        discounted = self.subtotal() - self.discount()
        return discounted if discounted > 0 else Decimal('0.00')

    def total_plus_tax(self):
        return self.total() + self.taxes()


class ShoppingCartMiddleware(object):
    """Middleware to add a ``Cart`` object to the request.  Must come after the
    ``SiteDetectionMiddleware`` because the cart needs the site object to be
    able to keep transactions for different sites separate.  
    """
    def process_request(self, request):
        cookie_name, session_key = self._get_cookie_pair(request)
        # cart session id is passed as querystring when transferring to
        # <subdomain>.takeouttiger.com for secure purchasing
        if request.GET.get('cs'):
            session_key = request.GET['cs']
        if session_key:
            s, created = Session.objects.get_or_create(session_key=session_key, defaults=dict(
                session_data=Session.objects.encode({}), 
                expire_date=(datetime.now() + timedelta(days=7))
            ))
            request.cart = Cart(s)
        else:
            request.cart = None

    def process_response(self, request, response):
        cookie_name, session_key = self._get_cookie_pair(request)
        # special workaround for passing cart between domains
        if request.GET.get('cs'):
            session_key = request.GET['cs']
            response.set_cookie(str(cookie_name), session_key)
        elif session_key is None:
            session_key = hashlib.md5(
                cookie_name + settings.SECRET_KEY + str(time.time())
            ).hexdigest()
            Session.objects.create(
                session_key=session_key, 
                session_data=Session.objects.encode({}), 
                expire_date=(datetime.now() + timedelta(days=7)))
            response.set_cookie(str(cookie_name), session_key)
        return response

    def _get_cookie_pair(self, request):
        site = RequestSite(request)
        site_obj = site.get_site_object()
        if site_obj is None:
            # fake out the cookie setter if we're on takeouttiger.com
            return True, False
        cookie_name = 'takeouttiger_%s' % site.domain
        session_key = request.COOKIES.get(cookie_name)
        return cookie_name, session_key
