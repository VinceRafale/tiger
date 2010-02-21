from django.views.generic.simple import direct_to_template
from django.contrib.auth.decorators import login_required


@login_required
def dashboard(request):
    site = request.site
    specials = site.item_set.filter(special=True)
    return direct_to_template(request, template='dashboard/base.html', extra_context={
        'specials': specials,
    })


