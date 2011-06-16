from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.simple import direct_to_template

from tiger.accounts.forms import DomainForm, GoogleToolsForm
from tiger.content.forms import *
from tiger.content.models import *

from tiger.utils.views import add_edit_site_object, delete_site_object

@login_required
def home(request):
    return direct_to_template(request, template='dashboard/content/content.html', extra_context={
        'pdfs': request.site.pdfmenu_set.all()
    })

@login_required
def add_edit_pdf(request, pdf_id=None):
    instance = None
    if pdf_id is not None:
        instance = PdfMenu.objects.get(id=pdf_id)
        if instance.site != request.site:
            raise Http404
    if request.method == 'POST':
        form = PdfMenuForm(request.POST, site=request.site, instance=instance)
        if form.is_valid():
            pdf = form.save(commit=False)
            pdf.site = request.site
            pdf.save()
            form.save_m2m()
            pdf.update()
            verb = 'edited' if instance else 'created'
            messages.success(request, 'PDF menu %s successfully.' % verb)
            return HttpResponseRedirect(reverse('dashboard_pdf_list'))
    else:
        form = PdfMenuForm(site=request.site, instance=instance)
    return direct_to_template(request, template='dashboard/content/pdf_form.html', extra_context={
        'form': form
    })

@login_required
def delete_pdf(request, pdf_id):
    return delete_site_object(request, PdfMenu, pdf_id, 'dashboard_pdf_list')

@login_required
def preview_pdf(request, pdf_id):
    pdf = PdfMenu.objects.get(id=pdf_id)
    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = 'filename=menu-preview.pdf'
    response.write(pdf.render())
    return response

@login_required
def feature_pdf(request):
    pdf_id = request.POST.get('id')
    pdf = PdfMenu.objects.get(id=pdf_id)
    pdf.featured = True if not pdf.featured else False
    pdf.save()
    if pdf.featured:
        PdfMenu.objects.exclude(id=pdf_id).update(featured=False)
    return HttpResponse('{"success": true, "class": "%s"}' % ('featured' if pdf.featured else 'not-featured'))

@login_required
def pdf_list(request):
    return direct_to_template(request, template='dashboard/content/pdf_list.html', extra_context={
        'pdfs': request.site.pdfmenu_set.all()
    })

@login_required
def img_list(request):
    return direct_to_template(request, template='dashboard/content/img_list.html', extra_context={
        'images': request.site.itemimage_set.all()
    })

@login_required
def add_img(request):
    return add_edit_site_object(request, ItemImage, AddImageForm, 
        'dashboard/content/img_form.html', 'dashboard_img_list')

@login_required
def edit_img(request, img_id):
    return add_edit_site_object(request, ItemImage, EditImageForm, 
        'dashboard/content/img_form.html', 'dashboard_img_list', object_id=img_id)

@login_required
def delete_img(request, img_id):
    return delete_site_object(request, ItemImage, img_id, 'dashboard_img_list')

@login_required
def custom_domain(request):
    if request.method == 'POST':
        form = DomainForm(request.POST, instance=request.site)
        if form.is_valid():
            form.save()
            messages.success(request, 'Custom domain added successfully.')
    else:
        form = DomainForm(instance=request.site)
    return direct_to_template(request, template='dashboard/content/custom_domain.html', extra_context={
        'form': form,
        'NGINX_IP_ADDRESS': settings.NGINX_IP_ADDRESS
    })

@login_required
def get_images(request):
    list_items = ''.join([
        '<li><a href="#" id="%d"><img src="%s" /></a></li>' % (img.id, img.thumb.url)
        for img in request.site.itemimage_set.all()
    ])
    content = '<ul id="images">%s</ul>' % list_items
    if not list_items:
        content = '<p>You currently do not have any images in your image library. You can <a class="closing-link" href="%s" target="_blank">add one</a> now.' % reverse('dashboard_add_img')
    return HttpResponse(content)

@login_required
def look_docs(request):
    return direct_to_template(request, template='dashboard/content/look_docs.html')
    
@login_required
def google(request):
    if request.method == 'POST':
        form = GoogleToolsForm(request.POST, instance=request.site)
        if form.is_valid():
            form.save()
            messages.success(request, 'Google tools settings changed successfully.')
    else:
        form = GoogleToolsForm(instance=request.site)
    return direct_to_template(request, template='dashboard/content/google.html', extra_context={
        'form': form
    })
