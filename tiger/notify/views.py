import httplib
import datetime
import cgi

import oauth2 as oauth

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic.simple import direct_to_template

from tiger.notify.models import Fax, Social, Release
from tiger.utils.views import render_custom

TWITTER_REQUEST_TOKEN_URL = 'https://twitter.com/oauth/request_token'
TWITTER_AUTHORIZATION_URL = 'https://twitter.com/oauth/authenticate'
TWITTER_ACCESS_TOKEN_URL = 'https://twitter.com/oauth/access_token'


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


def twitter_connect(request):
    consumer = oauth.Consumer(settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET)
    client = oauth.Client(consumer)
    response, content = client.request(TWITTER_REQUEST_TOKEN_URL, "GET")
    if response['status'] != '200':
        raise Exception("Invalid response from Twitter.")
    # Step 2. Store the request token in a session for later use.
    request.session['twitter_unauthed_token'] = dict(cgi.parse_qsl(content))
    # Step 3. Redirect the user to the authentication URL.
    url = "%s?oauth_token=%s" % (TWITTER_AUTHORIZATION_URL,
        request.session['twitter_unauthed_token']['oauth_token'])
    return HttpResponseRedirect(url)


def twitter_return(request):
    consumer = oauth.Consumer(settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET)
    token = oauth.Token(request.session['twitter_unauthed_token']['oauth_token'],
        request.session['twitter_unauthed_token']['oauth_token_secret'])
    client = oauth.Client(consumer, token)
    resp, content = client.request(TWITTER_ACCESS_TOKEN_URL, "GET")
    if resp['status'] != '200':
        raise Exception("Invalid response from Twitter.")
    access_token = dict(cgi.parse_qsl(content))
    try:
        social = Social.objects.get(twitter_screen_name=access_token['screen_name'])
    except Social.DoesNotExist:
       return direct_to_template(request, template='notify/bad_twitter_name.html')
    social.twitter_token = access_token['oauth_token']
    social.twitter_secret = access_token['oauth_token_secret']
    social.save()
    return HttpResponseRedirect(str(social.site) + reverse('dashboard_marketing', urlconf='tiger.urls')) 


def press_list(request):
    return render_custom(request, 'notify/press_list.html', 
        {'releases': request.site.release_set.filter(visible=True).order_by('-time_sent')})

def press_detail(request, object_id, slug):
    press = get_object_or_404(Release, id=object_id, site=request.site, visible=True)
    return render_custom(request, 'notify/press_detail.html', 
        {'release': press})
