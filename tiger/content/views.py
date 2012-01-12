from django.shortcuts import get_object_or_404

from tiger.content.models import ItemImage, Content, MenuItem
from tiger.utils.views import render_custom


def home(request):
    page = MenuItem.objects.get(position=1, site=request.site).page
    return render_custom(request, 'content/page.html', {'page': page})


def page_detail(request, id, slug):
    page = Content.objects.get(site=request.site, id=id)
    return render_custom(request, 'content/page.html', {'page': page})


def image_detail(request, image_id, slug):
    img = get_object_or_404(ItemImage, id=image_id, site=request.site)
    return render_custom(request, 'content/image_detail.html', {'img': img})    
