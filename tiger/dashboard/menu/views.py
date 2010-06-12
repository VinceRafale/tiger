import json

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db.models import get_model
from django.forms.models import inlineformset_factory
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template.loader import render_to_string
from django.views.generic.simple import direct_to_template

from tiger.core.forms import *
from tiger.core.models import *
from tiger.accounts.forms import TimeSlotForm
from tiger.accounts.models import TimeSlot
from tiger.utils.forms import RequireOneFormSet
from tiger.utils.views import add_edit_site_object, delete_site_object
from tiger.utils.hours import *

def _reorder_objects(model, id_list):
    for i, obj_id in enumerate(id_list):
        obj = model.objects.get(id=obj_id)
        obj.ordering = i + 1
        obj.save()

@login_required
def section_list(request):
    site = request.site
    return direct_to_template(request, template='dashboard/menu/section_list.html', extra_context={
        'sections': site.section_set.all()
    })

@login_required
def view_menu(request, object_type, object_id):
    model = get_model('core', object_type)
    site = request.site
    instance = get_object_or_404(model, id=object_id)
    if instance.site != site:
        raise Http404()
    return direct_to_template(request, template='dashboard/menu/%s_form_base.html' % object_type, 
        extra_context={'object': instance, 'type': object_type})

@login_required
def add_edit_menu(request, object_type, object_id=None):
    model = get_model('core', object_type)
    form_dict = {
        'section': SectionForm,
        'item': get_item_form(request.site)
    }
    instance = None
    form_class = form_dict[object_type]
    if object_id is not None:
        instance = get_object_or_404(model, id=object_id)
    if instance and instance.site != request.site:
        raise Http404()
    if request.method == 'POST':
        form = form_class(request.POST, instance=instance)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.site = request.site
            obj.save()
            return HttpResponseRedirect(reverse('dashboard_view_menu', args=[object_type, obj.id]))
    else:
        form_kwds = {}
        if all([instance is None, request.GET.get('pk'), model == Item]):
            form_kwds['initial'] = {'section': request.GET['pk'], 'taxable': True}
        form = form_class(instance=instance, **form_kwds)
    return direct_to_template(request, template='dashboard/menu/%s_form.html' % object_type, extra_context={
        'form': form,
        'object': instance,
        'type': object_type
    })

def add_related(request, object_type, object_id, form_class):
    if not request.is_ajax() or request.method != 'POST':
        raise Http404
    model = get_model('core', object_type)
    instance = get_object_or_404(model, id=object_id)
    form = form_class(request.POST)
    if form.is_valid():
        obj = form.save(commit=False)
        setattr(obj, object_type, instance)
        obj.save()
        row = render_to_string('dashboard/menu/includes/%s_row.html' % obj.__class__.__name__.lower(), {
            'obj': obj,    
            'MEDIA_URL': settings.MEDIA_URL
        })
        result = {
            'new_row': row
        }
    else:
        result = {'errors': form._errors}
    return HttpResponse(json.dumps(result))

@login_required
def add_pricepoint(request, object_type, object_id):
    return add_related(request, object_type, object_id, VariantForm)

@login_required
def add_extra(request, object_type, object_id):
    return add_related(request, object_type, object_id, UpgradeForm)

@login_required
def add_sidegroup(request, object_type, object_id):
    if not request.is_ajax() or request.method != 'POST':
        raise Http404
    result = {}
    try:
        model = get_model('core', object_type)
        instance = get_object_or_404(model, id=object_id)
        group = SideDishGroup()
        setattr(group, object_type, instance)
        group.save()
        result['success'] = True
        result['new_row'] = render_to_string('dashboard/menu/includes/group_row.html', {
            'group': group,
            'MEDIA_URL': settings.MEDIA_URL
        })
    except:
        result['success'] = False
    return HttpResponse(json.dumps(result))

@login_required
def add_side(request, object_id, instance=None):
    if not request.is_ajax() or request.method != 'POST':
        raise Http404
    instance = get_object_or_404(SideDishGroup, id=object_id)
    form = SideDishForm(request.POST)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.group = instance
        obj.save()
        row = render_to_string('dashboard/menu/includes/side_row.html', {
            'obj': obj,
            'MEDIA_URL': settings.MEDIA_URL
        })
        result = {
            'new_row': row
        }
    else:
        result = {'errors': form._errors}
    return HttpResponse(json.dumps(result))

def edit_related(request, item_id, model, form_class, attr_list, object_type):
    instance = model.objects.get(id=item_id)
    if request.method == 'GET':
        initial = {}
        for attr in attr_list:
            val = getattr(instance, attr, '')
            initial[attr] = str(val) if val else ''
        return HttpResponse(json.dumps(initial))
    form = form_class(request.POST, instance=instance)
    if form.is_valid():
        obj = form.save()
        row = render_to_string('dashboard/menu/includes/%s_row.html' % object_type, {
            'obj': obj    
        })
        result = {
            'new_row': row
        }
    else:
        result = {'errors': form._errors}
    return HttpResponse(json.dumps(result))

@login_required
def edit_pricepoint(request, item_id):
    return edit_related(request, item_id, Variant, VariantForm, ('description', 'price',), 'variant')

@login_required
def edit_side(request, item_id):
    return edit_related(request, item_id, SideDish, SideDishForm, ('name', 'price',), 'side')

@login_required
def edit_extra(request, item_id):
    return edit_related(request, item_id, Upgrade, UpgradeForm, ('name', 'price',), 'upgrade')

def delete_object(model, object_id):
    try:
        obj = model.objects.get(id=object_id)
        obj.delete()
    except:
        deleted = False
    else:
        deleted = True
    return HttpResponse(json.dumps({'deleted': deleted}))

@login_required
def delete_pricepoint(request, object_id):
    return delete_object(Variant, object_id)

@login_required
def delete_extra(request, object_id):
    return delete_object(Upgrade, object_id)

@login_required
def delete_sidegroup(request, object_id):
    return delete_object(SideDishGroup, object_id)

@login_required
def delete_side(request, object_id):
    return delete_object(SideDish, object_id)

@login_required
def delete_section(request, section_id):
    return delete_site_object(request, Section, section_id, 'dashboard_menu')

@login_required
def reorder_sections(request):
    section_ids = request.POST.getlist('section_ids')
    _reorder_objects(Section, section_ids)
    return HttpResponse('')

@login_required
def delete_item(request, item_id):
    return delete_site_object(request, Item, item_id, 'dashboard_menu')

@login_required
def reorder_items(request):
    item_ids = request.POST.getlist('item_ids')
    _reorder_objects(Item, item_ids)
    return HttpResponse('')

@login_required
def flag_item(request):
    lookup, val = request.POST.items()[0]
    attr, pk = lookup.split('-')
    item = Item.objects.get(id=pk)
    setattr(item, attr, True if val == 'true' else False)
    item.save()
    return HttpResponse('')

@login_required
def section_hours(request, section_id):
    #TODO: make this DRY with the restaurant hours view
    section = Section.objects.get(id=section_id)
    def get_forms(data=None):
        forms = []
        for dow, label in DOW_CHOICES:
            try:
                instance = TimeSlot.objects.get(site=request.site, section=section, dow=dow)
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
            messages.success(request, 'Hours updated successfully.')
            return HttpResponseRedirect(reverse('dashboard_view_menu', args=['section', section.id]))
    else:
        forms = get_forms()
    form_list = zip([label for dow, label in DOW_CHOICES], forms)
    return direct_to_template(request, template='dashboard/restaurant/hours.html', extra_context={'form_list': form_list, 'section': section})
