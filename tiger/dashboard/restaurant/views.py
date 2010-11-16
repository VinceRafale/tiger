from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic.create_update import update_object
from django.views.generic.simple import direct_to_template

from tiger.accounts.forms import LocationForm, TimeSlotForm
from tiger.accounts.models import TimeSlot, Schedule, Location
from tiger.content.forms import ContentForm
from tiger.content.models import Content
from tiger.utils.hours import *
from tiger.utils.views import add_edit_site_object


@login_required
def home(request):
    return direct_to_template(request, template='dashboard/restaurant/home.html', extra_context={}) 

@login_required
def location_list(request):
    #return direct_to_template(request, template='dashboard/restaurant/location_list.html', extra_context={})
    location = request.location
    return add_edit_site_object(request, Location, LocationForm, 'dashboard/restaurant/location_form.html', 'dashboard_location', object_id=location.id)

@login_required
def add_location(request):
    return add_edit_site_object(request, Location, LocationForm, 'dashboard/restaurant/location_form.html', 'dashboard_location', pass_site_to_form=True)
    
@login_required
def edit_location(request, location_id):
    return add_edit_site_object(request, Location, LocationForm, 'dashboard/restaurant/location_form.html', 'dashboard_location', object_id=location_id, pass_site_to_form=True)

@login_required
def delete_location(request, location_id):
    location = Location.objects.get(id=location_id)
    location.delete()
    messages.success(request, 'Location deleted successfully.')
    return HttpResponseRedirect(reverse('dashboard_location'))

@login_required
def edit_content(request, slug):
    instance = Content.objects.get(site=request.site, slug=slug)
    if request.method == 'POST':
        form = ContentForm(request.POST, site=request.site, instance=instance)
        if form.is_valid():
            content = form.save(commit=False)
            content.site = request.site
            content.save()
            messages.success(request, 'Content updated successfully.')
            return HttpResponseRedirect(reverse('dashboard_content'))
    else:
        form = ContentForm(site=request.site, instance=instance)
    return direct_to_template(request, template='dashboard/content/%s_form.html' % slug, extra_context={
        'form': form
    })

@login_required
def schedule_list(request):
    schedules = request.site.schedule_set.all()
    return direct_to_template(request, template='dashboard/restaurant/schedule_list.html', extra_context={
        'schedules': schedules
    })

@login_required
def add_edit_schedule(request, schedule_id=None):
    schedule = None
    if schedule_id is not None:
        schedule = Schedule.objects.get(id=schedule_id)
    def get_forms(data=None):
        forms = []
        for dow, label in DOW_CHOICES:
            instance = None
            if schedule is not None:
                try:
                    instance = TimeSlot.objects.get(schedule=schedule, dow=dow)
                except TimeSlot.DoesNotExist:
                    instance = None
            form = TimeSlotForm(data=data, instance=instance, prefix=dow)
            forms.append(form)
        return forms
    if request.method == 'POST':
        forms = get_forms(request.POST)
        if all(form.is_valid() for form in forms):
            if schedule is None:
                schedule = Schedule.objects.create(site=request.site)
            for dow, form in zip([dow for dow, label in DOW_CHOICES], forms):
                instance = form.save()
                # overridden save() will return None if no times are given for a day
                if instance is not None:
                    instance.dow = dow
                    instance.schedule = schedule
                    instance.save()
            display_hours = request.POST.get('hours_display')
            schedule.display = display_hours or calculate_hour_string(schedule.timeslot_set.all())
            schedule.save()
            messages.success(request, 'Hours updated successfully.')
            return HttpResponseRedirect(reverse('edit_hours'))
    else:
        forms = get_forms()
    form_list = zip([label for dow, label in DOW_CHOICES], forms)
    extra_context = {'form_list': form_list, 'schedule': schedule}
    return direct_to_template(request, template='dashboard/restaurant/hours.html', extra_context=extra_context)

@login_required
def delete_schedule(request, schedule_id):
    schedule = Schedule.objects.get(id=schedule_id)
    if any([
        getattr(schedule, '%s_set' % related).count()
        for related in ('location', 'section', 'item', 'variant',)
    ]):
        messages.error(request, 'You cannot delete a schedule when it is in use.  Please first remove it from all locations, menu sections and items, and pricepoints.')
    else:
        schedule.delete()
        messages.success(request, 'Schedule deleted successfully.')
    return HttpResponseRedirect(reverse('edit_hours'))


@login_required
def toggle_order_status(request):
    site = request.site
    if not site.ordersettings.can_receive_orders():
        messages.error(request, "You must enter a fax number or e-mail address to receive online orders.") 
        return HttpResponseRedirect(reverse('order_options'))
    if not site.ordersettings.tax_rate:
        messages.error(request, "You must enter a sales tax rate to receive online orders.") 
        return HttpResponseRedirect(reverse('dashboard_location'))
    if site.enable_orders:
        site.enable_orders = False
    else:
        site.enable_orders = True
    site.save()
    return HttpResponseRedirect(reverse('dashboard_orders'))

@login_required
def fetch_hours(request):
    forms = []
    for dow, label in DOW_CHOICES:
        form = TimeSlotForm(request.POST, prefix=dow)
        forms.append(form)
    if all(form.is_valid() for form in forms):
        instances = []
        for dow, form in zip([dow for dow, label in DOW_CHOICES], forms):
            instance = form.save(commit=False)
            if instance:
                instance.dow = dow
                instances.append(instance)
        hour_string = calculate_hour_string(instances)
        return HttpResponse(hour_string)
    else:
        return HttpResponse('')
