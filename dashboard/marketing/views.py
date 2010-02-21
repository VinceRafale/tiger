from datetime import datetime
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db.models import Sum
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.list_detail import object_list
from django.views.generic.simple import direct_to_template

from tiger.accounts.forms import *
from tiger.accounts.models import *
from tiger.notify.forms import TwitterForm, BlastForm
from tiger.notify.models import Fax, Blast
from tiger.utils.pdf import render_to_pdf
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
    return direct_to_template(request, template='dashboard/marketing/home.html', extra_context={
        'email_subscribers': email_subscribers,
        'fax_subscribers': fax_subscribers,
        'total_pages': total_pages,
        'pages_for_month': pages_for_month,
        'blasts': site.blast_set.all()
    })

@login_required
def add_edit_blast(request, blast_id=None):
    return add_edit_site_object(request, Blast, BlastForm, 
        'dashboard/marketing/blast_form.html', 'dashboard_marketing', object_id=blast_id)

@login_required
def delete_blast(request, blast_id):
    return delete_site_object(request, Blast, blast_id, 'dashboard_marketing')

@login_required
def send_blast(request, blast_id):
    blast = Blast.objects.get(id=blast_id, site=request.site)
    blast.send()
    messages.success(request, 'Blast "%s" has been started.' % blast.name)
    return delete_site_object(request, Blast, blast_id, 'dashboard_marketing')


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

