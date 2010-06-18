from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic.create_update import update_object
from django.views.generic.simple import direct_to_template

from tiger.accounts.forms import LocationForm, TimeSlotForm
from tiger.accounts.models import TimeSlot
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
        

def save_hours(request, section=None, instance_kwds={}, extra_context={}, redirect_to=None):
    def get_forms(data=None):
        forms = []
        for dow, label in DOW_CHOICES:
            try:
                instance = TimeSlot.objects.get(site=request.site, dow=dow, **instance_kwds)
            except TimeSlot.DoesNotExist:
                instance = None
            form = TimeSlotForm(data=data, instance=instance, prefix=dow)
            forms.append(form)
        return forms
    if request.method == 'POST':
        forms = get_forms(request.POST)
        if all(form.is_valid() for form in forms):
            for dow, form in zip([dow for dow, label in DOW_CHOICES], forms):
                instance = form.save()
                # overridden save() will return None if no times are given for a day
                if instance is not None:
                    instance.dow = dow
                    instance.site = request.site
                    instance.section = section
                    instance.save()
            display_hours = request.POST.get('hours_display')
            if section:
                section.hours = display_hours
                section.save()
            else:
                request.site.hours = display_hours
                request.site.save()
            messages.success(request, 'Hours updated successfully.')
            return HttpResponseRedirect(redirect_to)
    else:
        forms = get_forms()
    form_list = zip([label for dow, label in DOW_CHOICES], forms)
    context = {'form_list': form_list}
    context.update(extra_context)
    return direct_to_template(request, template='dashboard/restaurant/hours.html', extra_context=context)

@login_required
def edit_hours(request):
    return save_hours(request, instance_kwds={'section__isnull': True}, redirect_to=reverse('dashboard_menu'))

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
        messages.warning(request, "You have disabled online orders.") 
    else:
        site.enable_orders = True
        messages.success(request, "You are now taking orders online.") 
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
