from django.http import HttpResponseNotFound, HttpResponseServerError, Http404
from django.template import loader, RequestContext
from django.views.generic.simple import direct_to_template

from tiger.utils.template import load_custom


def render_custom(request, template, context):
    t = load_custom(request, template)
    c = RequestContext(request, context)
    return t.render(c)
    
def handler404(request):
    t = render_custom(request, '404.html')
    return HttpResponseNotFound(t)

def handler500(request):
    t = render_custom(request, '500.html')
    return HttpResponseServerError(t)


def add_edit_site_object(request, model, form_class, template, object_id=None):
    instance = None
    site = request.site
    if site.account.user != request.user:
        raise Http404()
    if object_id is not None:
        instance = model.objects.get(id=object_id)
        if instance.site != site:
            raise Http404()
    if request.method == 'POST':
        form = form_class(request.POST, instance=instance)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.site = site
            obj.save()
            return HttpResponseRedirect(reverse('dashboard_menu'))
    else:
        form = form_class(instance=instance)
    return direct_to_template(request, template=template, extra_context={
        'form': form
    })


def delete_site_object(request, model, object_id):
    site = request.site
    if site.account.user != request.user:
        raise Http404()
    instance = model.objects.get(id=object_id)
    if instance.site != site:
        raise Http404()
    instance.delete()
    return HttpResponseRedirect(reverse('dashboard_menu'))
