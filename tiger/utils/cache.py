from django.conf import settings
from django.core.cache import cache


def cachedmethod(cacheproxy):
    def wrap(method):
        def wrapped(*args, **kwargs):
            instance, args = args[0], args[1:] 
            key = cacheproxy.key(instance.id)
            cached_val = cache.get(key)
            if cached_val is not None:
                return cached_val
            val = method(instance, *args, **kwargs)
            cache.set(key, val, 60 * 60 * 24 * 7)
            return val
        return wrapped
    return wrap



class CacheProxy(object):
    def __init__(self, key_template):
        self.key_template = key_template
        pass

    def key(self, id):
        return self.key_template % id

    def invalidate(self, id):
        cache.delete(self.key(id))


class KeyChainMetaclass(type):
    def __new__(cls, name, bases, dct):
        """Sets cache key templates declared in settings as class
        attributes.
        """
        new_class = super(KeyChainMetaclass, cls).__new__(cls, name, bases, dct)
        cache_keys = getattr(settings, 'KEYCHAIN_CACHE_KEYS', {})
        for k, v in cache_keys.items():
            setattr(new_class, k, v)
        return new_class

    def __getattr__(cls, name):
        try:
            key_template = getattr(cls, 'KEY_%s' % name.upper())
        except AttributeError:
            raise AttributeError('No key template defined for %s' % name)
        return CacheProxy(key_template)
        

class KeyChain(object):
    __metaclass__ = KeyChainMetaclass
