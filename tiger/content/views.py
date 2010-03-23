from django.shortcuts import get_object_or_404

from tiger.content.models import ItemImage
from tiger.utils.views import render_custom


def image_detail(request, image_id, slug):
    img = get_object_or_404(ItemImage, id=image_id, site=request.site)
    return render_custom(request, 'content/image_detail.html', {'img': img})    
