import json
from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db.models import Sum
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.views.generic.list_detail import object_list
from django.views.generic.simple import direct_to_template
from django.utils.safestring import mark_safe

import facebook
from markdown import markdown

from tiger.accounts.forms import *
from tiger.accounts.models import *
from tiger.core.forms import CouponCreationForm
from tiger.core.models import Coupon
from tiger.notify.forms import *
from tiger.notify.models import Fax, Release
from tiger.notify.tasks import PublishTask
from tiger.utils.cache import KeyChain
from tiger.utils.views import add_edit_site_object, delete_site_object

@login_required
def home(request):
    site = request.site
    total_pages = Fax.objects.filter(site=site).aggregate(Sum('page_count'))['page_count__sum']
    this_month = datetime(datetime.now().year, datetime.now().month, 1)
    pages_for_month = Fax.objects.filter(
        site=site, completion_time__gte=this_month).aggregate(Sum('page_count'))['page_count__sum']
    return direct_to_template(request, template='dashboard/marketing/integrations.html', extra_context={
        'FB_API_KEY': settings.FB_API_KEY,
        'mailchimp_form': MailChimpForm(instance=site.social)
    })


@login_required
def integration_settings(request):
    data = json.loads(request.POST.get('data'))
    social = request.site.social
    for k, v in data.items():
        setattr(social, k, v)
    social.save()
    return HttpResponse(json.dumps({}))


@login_required
def publish_list(request):
    return direct_to_template(request, template='dashboard/marketing/publish_list.html', extra_context={
        'items': request.site.release_set.order_by('-time_sent')
    })
    
@login_required
def publish_detail(request, release_id):
    return add_edit_site_object(request, Release, UpdatePublishForm, 
        'dashboard/marketing/update_release_form.html', 'dashboard_publish', object_id=release_id)

@login_required
def publish_delete(request, release_id):
    KeyChain.news.invalidate(request.site.id)
    return delete_site_object(request, Release, release_id, 'dashboard_publish')

@login_required
def publish(request, release_id=None):
    if request.method == 'POST':
        form = PublishForm(request.POST, site=request.site)
        if form.is_valid():
            release = form.save(commit=False)
            release.site = request.site
            release.save()
            cleaned_data = form.cleaned_data
            PublishTask.delay(release.id, 
                twitter=cleaned_data.get('twitter'),
                fb=cleaned_data.get('facebook'),
                mailchimp=cleaned_data.get('mailchimp'),
                fax_list = cleaned_data.get('fax_list')
            )
            KeyChain.news.invalidate(request.site.id)
            messages.success(request, 'News item published successfully.')
            return HttpResponseRedirect(reverse('dashboard_publish'))
    else:
        form = PublishForm(site=request.site)
    return direct_to_template(request, template='dashboard/marketing/publish.html', extra_context={
        'form': form
    })

@login_required
def publish_preview(request):
    return HttpResponse(mark_safe(markdown(request.POST.get('preview', ''))))

@login_required
def coupon_list(request):
    return object_list(request, Coupon.objects.filter(site=request.site), 
        template_name='dashboard/marketing/coupon_list.html',
        extra_context={'coupons': request.site.coupon_set.all()})

@login_required
def add_edit_coupon(request, coupon_id=None):
    return add_edit_site_object(request, Coupon, CouponCreationForm, 
        'dashboard/marketing/coupon_form.html', 'dashboard_coupon_list', object_id=coupon_id)

@login_required
def delete_coupon(request, coupon_id):
    return delete_site_object(request, Coupon, coupon_id, 'dashboard_marketing')

@login_required
def fax_list(request):
    return object_list(request, FaxList.objects.filter(site=request.site), 
        template_name='dashboard/marketing/fax_list.html')

@login_required
def add_fax_list(request):
    if not request.is_ajax() or request.method != 'POST':
        raise Http404
    form = FaxListForm(request.POST)
    if form.is_valid():
        fax_list = form.save(commit=False)
        fax_list.site = request.site
        fax_list.save()
        html = render_to_string('dashboard/marketing/includes/fax_list_row.html',
            {'faxlist': fax_list})
        result = {
            'html': html
        }   
    else:
        result = {'errors': form._errors}
    return HttpResponse(json.dumps(result))

@login_required
def delete_fax_list(request, fax_list_id):
    fax_list = get_object_or_404(FaxList, id=fax_list_id)
    fax_list.delete()
    return HttpResponseRedirect(reverse('fax_list'))

@login_required
def fax_list_detail(request, fax_list_id):
    fax_list = get_object_or_404(FaxList, id=fax_list_id, site=request.site)
    return object_list(request, fax_list.subscriber_set.all(), 
        template_name='dashboard/marketing/subscriber_list.html', extra_context={
        'current_list': fax_list,
        'fax_lists': FaxList.objects.filter(site=request.site)
    })

@login_required
def add_edit_subscriber(request, fax_list_id, subscriber_id=None):
    instance = None
    if subscriber_id is not None:
        instance = Subscriber.objects.get(id=subscriber_id)
    if request.method == 'POST':
        form = SubscriberForm(request.POST, instance=instance, site=request.site)
        if form.is_valid():
            subscriber = form.save(commit=False)
            if instance is None:
                fax_list = FaxList.objects.get(id=fax_list_id)
                subscriber.fax_list = fax_list
            subscriber.save()
            msg= 'Subscriber %s successfully.' % ('edited' if instance else 'created')
            messages.success(request, msg)
            return HttpResponseRedirect(reverse('fax_list_detail', args=[subscriber.fax_list.id]))
    else:
        form = SubscriberForm(instance=instance, site=request.site)
    return direct_to_template(request, 
        template='dashboard/marketing/subscriber_form.html', 
        extra_context={
            'form': form
    })

@login_required
def delete_subscriber(request, fax_list_id, subscriber_id):
    fax_list = FaxList.objects.get(id=fax_list_id)
    if fax_list.site != request.site:
        raise Http404
    subscriber = Subscriber.objects.get(fax_list=fax_list, id=subscriber_id)
    subscriber.delete()
    messages.success(request, 'Subscriber deleted successfully.')
    return HttpResponseRedirect(reverse('fax_list_detail', args=[fax_list.id]))

@login_required
def fetch_coupon(request):
    coupon_id = request.GET.get('coupon')
    coupon = Coupon.objects.get(id=coupon_id)
    return HttpResponse(json.dumps({
        'boilerplate': coupon.boilerplate(),
        'short_url': unicode(request.site) + reverse('coupon_short_code', kwargs={'item_id': coupon_id})
    }))

###############################################################################
# TWITTER INTEGRATION VIEWS
###############################################################################

@login_required
def add_twitter(request):
    social = request.site.social
    if request.method == 'POST':
        form = TwitterForm(request.POST, instance=social)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('http://www.takeouttiger.com/twitter/connect/')
    else:
        form = TwitterForm(instance=social)
    return direct_to_template(request, template='dashboard/marketing/twitter_connect.html', 
        extra_context={'form': form})

@login_required
def remove_twitter(request):
    social = request.site.social
    social.twitter_token = ''
    social.twitter_secret = ''
    social.twitter_screen_name = ''
    social.save()
    return HttpResponseRedirect(reverse('dashboard_marketing'))


###############################################################################
# FACEBOOK INTEGRATION VIEWS
###############################################################################

@login_required
def get_facebook_pages_form(request):
    social = request.site.social
    social.facebook_url = social.facebook_page_token = ''
    social.facebook_page_name = ''
    social.save()
    pages = social.facebook_pages
    if len(pages) == 1:
        return HttpResponse(render_to_string(social.facebook_fragment, {
            'social': social,
            'errors': """Can't change pages - you currently only have 
                      one associated with your Facebook account."""
        }))
    if request.method == 'POST':
        page_id = request.POST.get('page')
        page = dict([
            (page['id'], page)
            for page in pages
        ])[page_id]
        social.facebook_url = page['link']
        social.facebook_page_token = page['access_token']
        social.facebook_page_name = page['name']
        social.save()
    return HttpResponse(render_to_string(social.facebook_fragment, {
        'social': social 
    }))
    

@login_required
def remove_facebook(request):
    social = request.site.social
    social.facebook_page_name = social.facebook_page_token = social.facebook_token = social.facebook_id = social.facebook_url = ''
    social.facebook_auto_items = False
    social.save()
    return HttpResponseRedirect(reverse('dashboard_marketing'))

@login_required
def register_id(request):
    cookie = facebook.get_user_from_cookie(
        request.COOKIES, settings.FB_API_KEY, settings.FB_API_SECRET)
    access_token = request.POST.get('accessToken')
    social = request.site.social
    social.facebook_token = access_token
    social.save()
    pages = social.facebook_pages
    return HttpResponse(render_to_string(social.facebook_fragment, {
        'social': social 
    }))

###############################################################################
# MAILCHIMP INTEGRATION VIEWS
###############################################################################

@login_required
def add_mailchimp_key(request):
    social = request.site.social
    social.mailchimp_api_key = request.POST.get('api_key')
    social.save()
    return HttpResponseRedirect(reverse('dashboard_marketing'))

@login_required
def get_mailchimp_lists(request):
    social = request.site.social
    return HttpResponse(social.get_mailchimp_lists())

@login_required
def set_mailchimp_list(request):
    #TODO: validation. Ajax.  Magicks.
    social = request.site.social
    list_id = request.POST.get('mail_list')
    social.mailchimp_list_id = list_id
    social.mailchimp_list_name = dict(social.mailchimp_lists)[list_id]
    social.mailchimp_from_email = request.POST.get('from_email')
    social.save()
    return HttpResponseRedirect(reverse('dashboard_marketing'))

@login_required
def edit_mailchimp_settings(request):
    social = request.site.social
    form = MailChimpForm(request.POST, instance=social)
    form.save()
    messages.success(request, 'MailChimp settings saved successfully.')
    return HttpResponseRedirect(reverse('dashboard_marketing'))
