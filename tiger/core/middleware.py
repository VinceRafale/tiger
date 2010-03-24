import hashlib
import time
from datetime import datetime, timedelta
from decimal import Decimal

from django.conf import settings
from django.contrib.sessions.models import Session

from tiger.accounts.middleware import DomainDetectionMiddleware
from tiger.core.forms import get_order_form
from tiger.core.models import Item


class Cart(object):
    contents = {}

    def __init__(self, session):
        self.session = session
        self.contents = session.get_decoded()

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
        cleaned_data['total'] = self.tally(cleaned_data)
        cleaned_data['name'] = '%s - %s' % (item.section.name, cleaned_data['name'])
        self[len(self) + 1] = cleaned_data

    def remove(self, key):
        self._pop(int(key))

    def clear(self):
        self._save({})

    def add_coupon(self, coupon):
        self['coupon'] = coupon.__dict__

    def remove_coupon(self, coupon):
        self._pop('coupon')
        
    @property
    def has_coupon(self):
        return 'coupon' in self

    def tally(self, item):
        qty = item['quantity']
        base_price = item['variant'].price
        upgrades = 0
        if item.has_key('upgrades'):
            upgrades = sum(upgrade.price for upgrade in item['upgrades'])
        return (base_price + upgrades) * qty

    def subtotal(self):
        return sum(item['total'] for k, item in self if type(k) == int)

    def discount(self):
        if not self.has_coupon:
            return 0
        percent = self['coupon']['discount'] / Decimal('100.00')
        return percent * self.subtotal()

    def total(self):
        return self.subtotal() - self.discount()


class ShoppingCartMiddleware(object):
    """Middleware to add a ``Cart`` object to the request.  Must come after the
    ``SiteDetectionMiddleware`` because the cart needs the site object to be
    able to keep transactions for different sites separate.  
    """
    def process_request(self, request):
        cookie_name, session_key = self._get_cookie_pair(request)
        if session_key:
            s, created = Session.objects.get_or_create(session_key=session_key, defaults=dict(
                session_data=Session.objects.encode({}), 
                expire_date=(datetime.now() + timedelta(days=7))
            ))
            request.cart = Cart(s)

    def process_response(self, request, response):
        cookie_name, session_key = self._get_cookie_pair(request)
        if session_key is None:
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
        site = DomainDetectionMiddleware.get_site(request)
        if site is None:
            # fake out the cookie setter if we're on takeouttiger.com
            return True, False
        cookie_name = 'takeouttiger_%s' % site.domain
        session_key = request.COOKIES.get(cookie_name)
        return cookie_name, session_key
