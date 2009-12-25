from django.http import HttpResponse
from tiger.core.models import Section, Item
from tiger.utils.views

def section_list(request):
    sections = Section.objects.filter(site=request.site)
    return HttpResponse(render_custom(request, 'core/section_list.html', 
        {'sections': sections}))

def section_detail(request, section):
    s = Section.objects.get(slug=section, site=request.site)
    return HttpResponse(render_custom(request, 'core/section_detail.html', 
        {'section': s}))

def item_detail(request, section, item):
    i = Item.objects.get(section__slug=section, slug=item, site=request.site)
    if request.method == 'POST':
        qty = request.POST.get('qty')
        request.cart.add(i.id, int(qty))
    return HttpResponse(render_custom(request, 'core/item_detail.html', 
        {'item': i}))


