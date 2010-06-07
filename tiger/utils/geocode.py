import urllib
import urllib2

from django.utils import simplejson

GEOCODE_URL = 'http://maps.google.com/maps/api/geocode/json'

class GeocodeError(Exception):
    pass

def geocode(address):
    params = {
        'sensor': 'false',
        'address': address
    }
    try:
        response = urllib2.urlopen('%s?%s' % (GEOCODE_URL, urllib.urlencode(params)))
        json = simplejson.loads(response.read())
        location = json['results'][0]['geometry']['location']
    except:
        raise GeocodeError
    lon = location['lng']
    lat = location['lat']
    return lon, lat
