from django.views.generic.simple import direct_to_template

from tiger.look.forms import SkinSelectForm

def picker(request):
    form = SkinSelectForm()
    return direct_to_template(request, template='dashboard/look/preview.html',
        extra_context={'form': form})
