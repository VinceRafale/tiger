from django.http import HttpResponse
from django.views.generic.simple import direct_to_template

from tiger.look.forms import SkinSelectForm
from tiger.look.models import Skin

def picker(request):
    form = SkinSelectForm()
    return direct_to_template(request, template='dashboard/look/preview.html',
        extra_context={'form': form})


def select_skin(request):
    skin_id = request.POST.get('id')
    skin = Skin.objects.get(id=skin_id)
    site = request.site
    site.skin = skin
    site.save()
    return HttpResponse("Your settings have been saved.")
