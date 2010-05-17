import httplib
import datetime

from oauth import oauth

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404

from tiger.notify.models import Fax, Social, Release
from tiger.notify.utils import *
from tiger.utils.views import render_custom

TWITTER_CONSUMER = oauth.OAuthConsumer(settings.TWITTER_CONSUMER_KEY, 
    settings.TWITTER_CONSUMER_SECRET)
TWITTER_CONNECTION = httplib.HTTPSConnection('twitter.com')
TWITTER_REQUEST_TOKEN_URL = 'https://twitter.com/oauth/request_token'
TWITTER_AUTHORIZATION_URL = 'https://twitter.com/oauth/authenticate'
TWITTER_ACCESS_TOKEN_URL = 'https://twitter.com/oauth/access_token'

signature_method = oauth.OAuthSignatureMethod_HMAC_SHA1()


def record_fax(request):
    transaction_id = request.POST.get('TransactionID')
    page_count = int(request.POST.get('PagesSent'))
    completion_time = request.POST.get('CompletionTime')
    destination = request.POST.get('DestinationFax')
    # convert odd date format of completion time to datetime object
    date_str, time_str = completion_time.split()
    date = datetime.date(*[int(s) for s in reversed(date_str.split('/'))])
    time = datetime.time(*[int(s) for s in time_str.split(':')])
    completion = datetime.datetime.combine(date, time)
    try:
        fax = Fax.objects.get(transaction=transaction_id)
    except Fax.DoesNotExist:
        parent_transaction_id = request.POST.get('ParentTransactionID')
        try:
            parent_fax = Fax.objects.get(transaction=parent_transaction_id)
        except Fax.DoesNotExist:
            return HttpResponse('')
        site = parent_fax.site
        Fax.objects.create(transaction=transaction_id, page_count=page_count, 
            parent_transaction=parent_transaction_id, site=site,
            completion_time=completion, destination=destination)
        return HttpResponse('')
    fax.page_count = page_count
    fax.completion_time = completion
    fax.destination = destination
    fax.save()
    return HttpResponse('')


def do_auth(request, consumer, connection, request_token_url, authorization_url, service, **kwargs):
    """Generates an unauthenticated token, stores it in the user's session,
    and redirects them to the authentication page for the given OAuth provider.
    """
    token = get_unauthorised_request_token(consumer, connection, request_token_url, **kwargs)
    auth_url = get_authorisation_url(consumer, token, authorization_url)
    response = HttpResponseRedirect(auth_url)
    request.session['%s_unauthed_token' % service] = token.to_string()   
    return response


def twitter_connect(request):
    return do_auth(request, TWITTER_CONSUMER, TWITTER_CONNECTION, TWITTER_REQUEST_TOKEN_URL, TWITTER_AUTHORIZATION_URL, 'twitter')


def get_access_token(request, consumer, connection, access_token_url, service, **kwargs):
    unauthed_token = request.session.get('%s_unauthed_token' % service)
    if not unauthed_token:
        return HttpResponse("No un-authed token cookie")
    token = oauth.OAuthToken.from_string(unauthed_token)   
    if token.key != request.GET.get('oauth_token', 'no-token'):
        return HttpResponse("Something went wrong! Tokens do not match")
    response = exchange_request_token_for_access_token(consumer, connection, token, access_token_url, **kwargs)
    return dict(s.split('=') for s in response.split('&'))


def twitter_return(request):
    auth_dict = get_access_token(request, TWITTER_CONSUMER, TWITTER_CONNECTION, TWITTER_ACCESS_TOKEN_URL, 'twitter')
    social = Social.objects.get(twitter_screen_name=auth_dict['screen_name'])
    social.twitter_token = auth_dict['oauth_token']
    social.twitter_secret = auth_dict['oauth_token_secret']
    social.save()
    return HttpResponseRedirect(str(social.site) + reverse('dashboard_marketing_home')) 

def press_detail(request, object_id, slug):
    press = get_object_or_404(Release, id=object_id, site=request.site)
    return render_custom(request, 'notify/press_detail.html', 
        {'release': press})
