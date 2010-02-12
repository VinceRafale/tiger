import json 

from django.conf import settings
from oauth import oauth

signature_method = oauth.OAuthSignatureMethod_HMAC_SHA1()

SERVER = getattr(settings, 'OAUTH_SERVER', 'twitter.com')
REQUEST_TOKEN_URL = getattr(settings, 'OAUTH_REQUEST_TOKEN_URL', 'https://%s/oauth/request_token' % SERVER)
ACCESS_TOKEN_URL = getattr(settings, 'OAUTH_ACCESS_TOKEN_URL', 'https://%s/oauth/access_token' % SERVER)
AUTHORIZATION_URL = getattr(settings, 'OAUTH_AUTHORIZATION_URL', 'http://%s/oauth/authenticate' % SERVER)

CONSUMER_KEY = getattr(settings, 'CONSUMER_KEY', 'YOUR_KEY')
CONSUMER_SECRET = getattr(settings, 'CONSUMER_SECRET', 'YOUR_SECRET')

# We use this URL to check if Twitters oAuth worked
TWITTER_CHECK_AUTH = 'https://twitter.com/account/verify_credentials.json'
TWITTER_FRIENDS = 'https://twitter.com/statuses/friends.json'

def request_oauth_resource(consumer, url, access_token, parameters=None, signature_method=signature_method, http_method="GET"):
    """
    usage: request_oauth_resource( consumer, '/url/', your_access_token, parameters=dict() )
    Returns a OAuthRequest object
    """
    oauth_request = oauth.OAuthRequest.from_consumer_and_token(
        consumer, token=access_token, http_method=http_method, http_url=url, parameters=parameters,
    )
    oauth_request.sign_request(signature_method, consumer, access_token)
    return oauth_request


def fetch_response(oauth_request, connection):
    url = oauth_request.to_url()
    connection.request(oauth_request.http_method, url)
    response = connection.getresponse()
    s = response.read()
    return s

def get_unauthorised_request_token(consumer, connection, request_token_url, signature_method=signature_method, **kwargs):
    oauth_request = oauth.OAuthRequest.from_consumer_and_token(
        consumer, http_url=request_token_url, parameters=kwargs
    )
    oauth_request.sign_request(signature_method, consumer, None)
    resp = fetch_response(oauth_request, connection)
    token = oauth.OAuthToken.from_string(resp)
    return token


def get_authorisation_url(consumer, token, authorization_url, signature_method=signature_method):
    oauth_request = oauth.OAuthRequest.from_consumer_and_token(
        consumer, token=token, http_url=authorization_url
    )
    oauth_request.sign_request(signature_method, consumer, token)
    return oauth_request.to_url()

def exchange_request_token_for_access_token(consumer, connection, request_token, access_token_url, signature_method=signature_method, **kwargs):
    oauth_request = oauth.OAuthRequest.from_consumer_and_token(
        consumer, token=request_token, http_url=access_token_url, parameters=kwargs
    )
    oauth_request.sign_request(signature_method, consumer, request_token)
    resp = fetch_response(oauth_request, connection)
    return resp

def is_authenticated(consumer, connection, access_token):
    oauth_request = request_oauth_resource(consumer, TWITTER_CHECK_AUTH, access_token)
    _json = fetch_response(oauth_request, connection)
    if 'screen_name' in _json:
        return _json
    return False
