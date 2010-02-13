from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db.models import Sum
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.list_detail import object_list
from django.views.generic.simple import direct_to_template

from tiger.accounts.forms import *
from tiger.accounts.models import *
from tiger.notify.forms import TwitterForm
from tiger.notify.models import Fax
from tiger.utils.pdf import render_to_pdf
from tiger.utils.views import add_edit_site_object, delete_site_object

@login_required
def home(request):
    site = request.site
    updates = site.scheduledupdate_set.all()
    email_subscribers = Subscriber.via_email.filter(site=site)
    fax_subscribers = Subscriber.via_fax.filter(site=site)
    total_pages = Fax.objects.filter(site=site).aggregate(Sum('page_count'))['page_count__sum']
    this_month = datetime(datetime.now().year, datetime.now().month, 1)
    pages_for_month = Fax.objects.filter(
        site=site, completion_time__gte=this_month).aggregate(Sum('page_count'))['page_count__sum']
    return direct_to_template(request, template='dashboard/marketing.html', extra_context={
        'updates': updates,
        'email_subscribers': email_subscribers,
        'fax_subscribers': fax_subscribers,
        'total_pages': total_pages,
        'pages_for_month': pages_for_month
    })

@login_required
def blast_list(request):
    site = request.site
    specials = site.scheduledupdate_set.all()
    return direct_to_template(request, template='dashboard/blast_list.html', extra_context={
        'updates': updates
    })

@login_required
def add_edit_blast(request, blast_id=None):
    return add_edit_site_object(request, ScheduledUpdate, ScheduledUpdateForm, 
        'dashboard/blast_form.html', 'dashboard_marketing', object_id=blast_id)

@login_required
def delete_blast(request, blast_id):
    return delete_site_object(request, ScheduledUpdate, blast_id, 'dashboard_marketing')

@login_required
def preview_blast(request, blast_id):
    update = ScheduledUpdate.objects.get(id=blast_id)
    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = 'filename=blast-preview.pdf'
    content = render_to_pdf('notify/update.html', {
        'specials': request.site.item_set.filter(special=True).order_by('section__id'),
        'footer': update.footer,
        'site': request.site,
        'show_descriptions': update.show_descriptions
    })
    response.write(content)
    return response

@login_required
def subscriber_list(request):
    return object_list(request, Subscriber.objects.filter(site=request.site), 
        template_name='dashboard/subscriber_list.html')

@login_required
def add_edit_subscriber(request, subscriber_id=None):
    return add_edit_site_object(request, Subscriber, SubscriberForm, 
        'dashboard/subscriber_form.html', 'dashboard_subscriber_list', object_id=subscriber_id)

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
    return direct_to_template(request, template='dashboard/twitter_connect.html', 
        extra_context={'form': form})

