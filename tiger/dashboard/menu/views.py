from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.forms.models import inlineformset_factory
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.views.generic.simple import direct_to_template

from tiger.core.forms import *
from tiger.core.models import *
from tiger.utils.forms import RequireOneFormSet
from tiger.utils.views import add_edit_site_object, delete_site_object

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
def add_edit_section(request, section_id=None):
    instance = None
    if section_id is not None:
        instance = get_object_or_404(Section, id=section_id)
    if instance and instance.site != request.site:
        raise Http404()
    if request.method == 'POST':
        form = SectionForm(request.POST, instance=instance)
        if form.is_valid():
            section = form.save(commit=False)
            section.site = request.site
            section.save()
            return HttpResponseRedirect(reverse('dashboard_view_section', args=[section.id]))
    else:
        form = SectionForm(instance=instance)
    return direct_to_template(request, template='dashboard/menu/section_form.html', extra_context={
        'form': form,
        'section': instance
    })

def edit_section_pricepoints(request, section_id):
    instance = get_object_or_404(Section, id=section_id)
    if instance.site != request.site:
        raise Http404()
    VariantFormSet = inlineformset_factory(Section, Variant, formset=RequireOneFormSet, extra=1)
    if request.method == 'POST':
        variant_formset = VariantFormSet(request.POST, instance=instance)
        if variant_formset.is_valid():
            variant_formset.save()
            return HttpResponseRedirect(reverse('dashboard_view_section', args=[instance.id]))
    else:
        variant_formset = VariantFormSet(instance=instance)
    return direct_to_template(request, template='dashboard/menu/section_pricepoints.html', extra_context={
        'formset': variant_formset,
        'section': instance
    })

def edit_section_sides(request, section_id):
    pass

def edit_section_extras(request, section_id):
    instance = get_object_or_404(Section, id=section_id)
    if instance.site != request.site:
        raise Http404()
    UpgradeFormSet = inlineformset_factory(Section, Upgrade, extra=1)
    if request.method == 'POST':
        upgrade_formset = UpgradeFormSet(request.POST, instance=instance)
        if upgrade_formset.is_valid():
            upgrade_formset.save()
            return HttpResponseRedirect(reverse('dashboard_view_section', args=[instance.id]))
    else:
        upgrade_formset = UpgradeFormSet(instance=instance)
    return direct_to_template(request, template='dashboard/menu/section_extras.html', extra_context={
        'formset': upgrade_formset,
        'section': instance
    })

@login_required
def delete_section(request, section_id):
    return delete_site_object(request, Section, section_id, 'dashboard_menu')

@login_required
def view_section(request, section_id):
    site = request.site
    instance = get_object_or_404(Section, id=section_id)
    if instance.site != site:
        raise Http404()
    return direct_to_template(request, template='dashboard/menu/section_form_base.html', 
        extra_context={'section': instance})

@login_required
def reorder_sections(request):
    section_ids = request.POST.getlist('section_ids')
    _reorder_objects(Section, section_ids)
    return HttpResponse('')

@login_required
def add_edit_item(request, item_id=None):
    instance = None
    site = request.site
    if site.account.user != request.user:
        raise Http404()
    if item_id is not None:
        instance = Item.objects.get(id=item_id)
        if instance.site != site:
            raise Http404()
    ItemForm = get_item_form(site)
    VariantFormSet = inlineformset_factory(Item, Variant, formset=RequireOneFormSet, extra=1)
    UpgradeFormSet = inlineformset_factory(Item, Upgrade, extra=1)
    if request.method == 'POST':
        form = ItemForm(request.POST, instance=instance)
        variant_formset = VariantFormSet(request.POST, instance=instance, prefix='variants')
        upgrade_formset = UpgradeFormSet(request.POST, instance=instance, prefix='upgrades')
        if all([form.is_valid(), variant_formset.is_valid(), upgrade_formset.is_valid()]):
            item = form.save(commit=False)
            item.site = site
            item.save()
            if instance is not None:
                variant_formset.save()
                upgrade_formset.save()
            else:
                for form in variant_formset.forms:
                    if form.has_changed():
                        variant = form.save(commit=False)
                        variant.item = item
                        variant.save()
                for form in upgrade_formset.forms:
                    if form.has_changed():
                        upgrade = form.save(commit=False)
                        upgrade.item = item
                        upgrade.save()
            return HttpResponseRedirect(reverse('dashboard_menu'))
    else:
        form_kwds = {}
        variant_formset = VariantFormSet(instance=instance, prefix='variants')
        upgrade_formset = UpgradeFormSet(instance=instance, prefix='upgrades')
        if instance is None:
            if request.GET.get('pk'):
                form_kwds['initial'] = {'section': request.GET['pk']}
            variant_formset.forms[0].fields['description'].initial = 'default'
        else:
            form_kwds['instance'] = instance 
        form = ItemForm(**form_kwds)
    return direct_to_template(request, template='dashboard/menu/item_form.html', extra_context={
        'form': form, 'variant_formset': variant_formset, 'upgrade_formset': upgrade_formset
    })

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
