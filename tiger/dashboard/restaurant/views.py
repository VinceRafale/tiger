from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic.create_update import update_object
from django.views.generic.simple import direct_to_template

from tiger.accounts.forms import LocationForm, TimeSlotForm
from tiger.accounts.models import TimeSlot, Schedule
from tiger.content.forms import ContentForm
from tiger.content.models import Content
from tiger.utils.hours import *


@login_required
def home(request):
    return direct_to_template(request, template='dashboard/restaurant/home.html', extra_context={
    })


@login_required
def location(request):
    return update_object(request, form_class=LocationForm, object_id=request.site.id, 
        template_name='dashboard/restaurant/location_form.html', post_save_redirect='/dashboard/restaurant/location/')
        

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
            schedule.display = display_hours
            schedule.save()
            messages.success(request, 'Hours updated successfully.')
            return HttpResponseRedirect(reverse('edit_hours'))
    else:
        forms = get_forms()
    form_list = zip([label for dow, label in DOW_CHOICES], forms)
    extra_context = {'form_list': form_list, 'schedule': schedule}
    return direct_to_template(request, template='dashboard/restaurant/hours.html', extra_context=extra_context)


@login_required
def toggle_order_status(request):
    site = request.site
    if not site.ordersettings.can_receive_orders():
        messages.error(request, "You must enter a fax number or e-mail address to receive online orders.") 
        return HttpResponseRedirect(reverse('order_options'))
    if not site.ordersettings.tax_rate:
        messages.error(request, "You must enter a sales tax rate to receive online orders.") 
        return HttpResponseRedirect(reverse('order_payment'))
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
