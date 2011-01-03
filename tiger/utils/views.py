from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseServerError, Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template import loader, RequestContext, Template
from django.utils.http import base36_to_int
from django.views.generic.simple import direct_to_template

from tiger.look.forms import *
from tiger.utils.template import load_custom
from tiger.stork import Stork


def render_custom(request, template, context=None):
    if context is None:
        context = {}
    # add toolbar if it's an authorized user
    if request.session.get('customizing'):
        if template == 'base.html':
            template = 'dashboard/look/preview.html'
        panels = Stork(request.site.theme)
        context.update({
            'styles': panels.style_tags(),
            'toolbar': panels.toolbar(),
            'base': 'dashboard/look/preview.html',
            'pre_base': panels['html-html'].as_template(staged=True),
        })
    else:
        context.update({
            'base': 'base.html',
            'pre_base': request.site.template()
        })
    t = load_custom(request, template)
    c = RequestContext(request, context)
    rendered = t.render(c)
    return HttpResponse(rendered)
    
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


def tiger404(request):
    return direct_to_template(request, 'tiger/404.html')

def tiger500(request):
    return direct_to_template(request, 'tiger/500.html')


def add_edit_site_object(request, model, form_class, template, reverse_on, object_id=None, pass_site_to_form=False):
    instance = None
    site = request.site
    if pass_site_to_form:
        kwds = {'site': site}
    else:
        kwds = {}
    if object_id is not None:
        instance = model.objects.get(id=object_id)
        if instance.site != site:
            raise Http404()
    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=instance, **kwds)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.site = site
            obj.save()
            form.save_m2m()
            verb = 'updated' if instance else 'created'
            msg = '%s "%s" has been %s successfully.' % (
                model._meta.verbose_name.capitalize(), unicode(obj), verb)
            messages.success(request, msg)
            return HttpResponseRedirect(reverse(reverse_on))
    else:
        form = form_class(instance=instance, **kwds)
    return direct_to_template(request, template=template, extra_context={
        'form': form,
        'instance': instance
    })


def delete_site_object(request, model, object_id, reverse_on):
    site = request.site
    instance = model.objects.get(id=object_id)
    if instance.site != site:
        raise Http404()
    instance.delete()
    return HttpResponseRedirect(reverse(reverse_on))


def short_code_redirect(request, item_id, model):
    item_id = base36_to_int(item_id)
    object = get_object_or_404(model, id=item_id, site=request.site)
    return HttpResponseRedirect(object.get_absolute_url())


def robots(request):
    return render_custom(request, 'robots.txt', {'site_name': request.META['HTTP_HOST']})
