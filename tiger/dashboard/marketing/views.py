import json
from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db.models import Sum
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.list_detail import object_list
from django.views.generic.simple import direct_to_template
from django.utils.safestring import mark_safe

from markdown import markdown

from tiger.accounts.forms import *
from tiger.accounts.models import *
from tiger.core.forms import CouponCreationForm
from tiger.core.models import Coupon
from tiger.notify.forms import *
from tiger.notify.models import Fax, Release
from tiger.utils.views import add_edit_site_object, delete_site_object

@login_required
def home(request):
    site = request.site
    email_subscribers = Subscriber.via_email.filter(site=site)
    fax_subscribers = Subscriber.via_fax.filter(site=site)
    total_pages = Fax.objects.filter(site=site).aggregate(Sum('page_count'))['page_count__sum']
    this_month = datetime(datetime.now().year, datetime.now().month, 1)
    pages_for_month = Fax.objects.filter(
        site=site, completion_time__gte=this_month).aggregate(Sum('page_count'))['page_count__sum']
    return direct_to_template(request, template='dashboard/marketing/integrations.html', extra_context={
        'FB_API_KEY': settings.FB_API_KEY,
        'mailchimp_form': MailChimpForm(instance=site.social)
    })

@login_required
def publish(request, release_id=None):
    return add_edit_site_object(request, Release, PublishForm, 
        'dashboard/marketing/publish.html', 'dashboard_marketing', object_id=release_id)

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
        'dashboard/marketing/coupon_form.html', 'dashboard_marketing', object_id=coupon_id)

@login_required
def delete_coupon(request, coupon_id):
    return delete_site_object(request, Coupon, coupon_id, 'dashboard_marketing')

@login_required
def subscriber_list(request):
    return object_list(request, Subscriber.objects.filter(site=request.site), 
        template_name='dashboard/marketing/subscriber_list.html')

@login_required
def add_edit_subscriber(request, subscriber_id=None):
    return add_edit_site_object(request, Subscriber, SubscriberForm, 
        'dashboard/marketing/subscriber_form.html', 'dashboard_subscriber_list', object_id=subscriber_id)

@login_required
def delete_subscriber(request, subscriber_id):
    return delete_site_object(request, Subscriber, subscriber_id, 'dashboard_subscriber_list')

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

def xd_receiver(request):
    return direct_to_template(request, template='dashboard/marketing/xd_receiver.htm')

def register_id(request):
    social = request.site.social
    social.facebook_id = request.POST.get('id')
    social.facebook_url = request.POST.get('url')
    social.save()
    return HttpResponse('')

def add_mailchimp_key(request):
    social = request.site.social
    social.mailchimp_api_key = request.POST.get('api_key')
    social.save()
    return HttpResponseRedirect(reverse('dashboard_marketing'))

def get_mailchimp_lists(request):
    social = request.site.social
    return HttpResponse(social.get_mailchimp_lists())

def set_mailchimp_list(request):
    social = request.site.social
    list_id = request.POST.get('mail_list')
    social.mailchimp_list_id = list_id
    social.mailchimp_list_name = dict(social.mailchimp_lists)[list_id]
    social.save()
    return HttpResponseRedirect(reverse('dashboard_marketing'))

def edit_mailchimp_settings(request):
    social = request.site.social
    form = MailChimpForm(request.POST, instance=social)
    form.save()
    messages.success(request, 'MailChimp settings saved successfully.')
    return HttpResponseRedirect(reverse('dashboard_marketing'))

def fetch_coupon(request):
    coupon_id = request.GET.get('coupon')
    coupon = Coupon.objects.get(id=coupon_id)
    return HttpResponse(json.dumps({
        'boilerplate': coupon.boilerplate(),
        'short_url': unicode(request.site) + reverse('coupon_short_code', kwargs={'item_id': coupon_id})
    }))
