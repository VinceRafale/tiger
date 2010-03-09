from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseServerError, Http404, HttpResponseRedirect
from django.template import loader, RequestContext
from django.views.generic.simple import direct_to_template

from tiger.utils.template import load_custom


def render_custom(request, template, context=None):
    t = load_custom(request, template)
    c = RequestContext(request, context)
    return HttpResponse(t.render(c))
    
def handler404(request):
    if request.path.startswith('/dashboard'):
        t = loader.render_to_string('tiger/404.html', {'MEDIA_URL': settings.MEDIA_URL})
    else:
        t = render_custom(request, '404.html')
    return HttpResponseNotFound(t)

def handler500(request):
    if request.path.startswith('/dashboard'):
        t = loader.render_to_string('tiger/500.html', {'MEDIA_URL': settings.MEDIA_URL})
    else:
        t = render_custom(request, '500.html')
    return HttpResponseServerError(t)


def add_edit_site_object(request, model, form_class, template, reverse_on, object_id=None):
    instance = None
    site = request.site
    if site.account.user != request.user:
        raise Http404()
    if object_id is not None:
        instance = model.objects.get(id=object_id)
        if instance.site != site:
            raise Http404()
    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.site = site
            obj.save()
            form.save_m2m()
            verb = 'updated' if instance else 'created'
            msg = '%s "%s" has been %s successfully.' % (
                model._meta.verbose_name, unicode(obj), verb)
            messages.success(request, msg)
            return HttpResponseRedirect(reverse(reverse_on))
    else:
        form = form_class(instance=instance)
    return direct_to_template(request, template=template, extra_context={
        'form': form,
        'instance': instance
    })


def delete_site_object(request, model, object_id, reverse_on):
    site = request.site
    if site.account.user != request.user:
        raise Http404()
    instance = model.objects.get(id=object_id)
    if instance.site != site:
        raise Http404()
    instance.delete()
    return HttpResponseRedirect(reverse(reverse_on))
