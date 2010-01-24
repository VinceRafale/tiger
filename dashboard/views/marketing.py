from django.contrib.auth.decorators import login_required
from django.views.generic.simple import direct_to_template

from tiger.accounts.forms import *
from tiger.accounts.models import *
from tiger.utils.views import add_edit_site_object

@login_required
def marketing_home(request):
    site = request.site
    updates = site.scheduledupdate_set.all()
    email_subscribers = Subscriber.via_email.filter(site=site)
    fax_subscribers = Subscriber.via_fax.filter(site=site)
    return direct_to_template(request, template='dashboard/marketing.html', extra_context={
        'updates': updates,
        'email_subscribers': email_subscribers,
        'fax_subscribers': fax_subscribers
    })

@login_required
def marketing_blast_list(request):
    site = request.site
    specials = site.scheduledupdate_set.all()
    return direct_to_template(request, template='dashboard/blast_list.html', extra_context={
        'updates': updates
    })

@login_required
def marketing_add_edit_blast(request, blast_id=None):
    return add_edit_site_object(request, ScheduledUpdate, ScheduledUpdateForm, 
        'dashboard/blast_form.html', object_id=blast_id)

@login_required
def marketing_delete_blast(request, blast_id):
    return delete_site_object(request, ScheduledUpdate, blast_id)

@login_required
def marketing_preview_blast(request, blast_id):
    pass

@login_required
def marketing_subscriber_list(request):
    pass

@login_required
def marketing_add_edit_subscriber(request, subscriber_id=None):
    return add_edit_site_object(request, Subscriber, SubscriberForm, 
        'dashboard/subscriber_form.html', object_id=subscriber_id)

@login_required
def marketing_delete_subscriber(request, subscriber_id):
    return delete_site_object(request, Subscriber, subscriber_id)

