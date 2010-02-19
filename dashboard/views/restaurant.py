from dateutil import parser, tz

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.create_update import update_object
from django.views.generic.simple import direct_to_template

from tiger.accounts.forms import LocationForm, TimeSlotForm
from tiger.accounts.models import TimeSlot, Site
from tiger.content.forms import ContentForm
from tiger.content.models import Content


def home(request):
    return direct_to_template(request, template='dashboard/restaurant.html', extra_context={
    })


def location(request):
    return update_object(request, form_class=LocationForm, object_id=request.site.id, 
        template_name='dashboard/location_form.html', post_save_redirect='/dashboard/restaurant/')
        

def edit_content(request, slug):
    c = Content.objects.get(site=request.site, slug=slug)
    return update_object(request, form_class=ContentForm, object_id=c.id, 
        template_name='dashboard/%s_form.html' % slug, post_save_redirect='/dashboard/restaurant/')
        

def edit_hours(request):
    def get_forms(data=None):
        forms = []
        for dow, label in TimeSlot.DOW_CHOICES:
            try:
                instance = TimeSlot.objects.get(site=request.site, dow=dow)
            except TimeSlot.DoesNotExist:
                instance = None
            form = TimeSlotForm(data=data, instance=instance, prefix=dow)
            forms.append(form)
        return forms
    if request.method == 'POST':
        forms = get_forms(request.POST)
        if all(form.is_valid() for form in forms):
            for dow, form in zip([dow for dow, label in TimeSlot.DOW_CHOICES], forms):
                instance = form.save()
                # overridden save() will return None if no times are given for a day
                if instance is not None:
                    instance.dow = dow
                    instance.site = request.site
                    instance.save()
    else:
        forms = get_forms()
    form_list = zip([label for dow, label in TimeSlot.DOW_CHOICES], forms)
    return direct_to_template(request, template='dashboard/hours.html', extra_context={'form_list': form_list})


def toggle_order_status(request):
    site = request.site
    if site.enable_orders:
        site.enable_orders = False
        messages.warning(request, "You have disabled online orders.") 
    else:
        site.enable_orders = True
        messages.success(request, "You are now taking orders online.") 
    site.save()
    return HttpResponseRedirect(reverse('dashboard_restaurant'))
