from dateutil import parser, tz

from django.http import HttpResponse
from django.views.generic.create_update import update_object
from django.views.generic.simple import direct_to_template

from tiger.accounts.forms import LocationForm
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
        

def create_update_timeslot(request, get_id=False):
    if request.method != 'POST':
        raise Http404
    start = parser.parse(request.POST['start'])
    stop = parser.parse(request.POST['end'])
    if get_id:
        timeslot = TimeSlot.objects.get(id=request.POST['id'])
    else:
        timeslot = TimeSlot(site=request.site)
    timeslot.start = start.strftime('%H:%M')
    timeslot.stop = stop.strftime('%H:%M')
    timeslot.dow = start.weekday()
    timeslot.save()
    return HttpResponse('')

def save_timeslot(request):
    return create_update_timeslot(request)
    
def update_timeslot(request):
    return create_update_timeslot(request, get_id=True)

def delete_timeslot(request):
    timeslot = TimeSlot.objects.get(id=request.POST['id'])
    timeslot.delete()
    return HttpResponse('')
