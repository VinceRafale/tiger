class Cart(object):
    contents = {}
    model = None

    def __get__(self, request, obj_type=None):
        session = self._session = request.session
        site = self._site = request.site
        if hasattr(session, '_cart_contents'):
            self.contents = session['_cart_contents']
        else:
            session['_cart_contents'] = {}

    def __iter__(self):
        return iter((self.model.objects.get(id=k), v) for k, v in self.contents.items())

    def __len__(self):
        return len(self.contents)

    def add(self, obj_id, qty):
        contents = self.contents
        if contents.has_key(obj_id):
            contents[obj_id] = contents[obj_id] + qty
        else:
            contents[obj_id] = qty
        self._session['_cart_contents'] = contents

    def remove(self, obj_id):
        contents = self.contents
        contents.pop(obj_id, None)
        self._session['_cart_contents'] = contents

    def clear(self):
        self._session['_cart_contents'] = {}


class ShoppingCartMiddleware(object):
    """Middleware to add a ``Cart`` object to the request.  Must come after the
    ``SiteDetectionMiddleware`` because the cart needs the site object to be
    able to keep transactions for different sites separate.  
    """
    def process_request(self, request):
        request.__class__.cart = Cart()
    
