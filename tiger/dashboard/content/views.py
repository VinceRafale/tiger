from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.simple import direct_to_template

from tiger.accounts.forms import DomainForm
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
            verb = 'edited' if instance else 'created'
            messages.success(request, 'PDF menu %s successfully.' % verb)
            return HttpResponseRedirect(reverse('dashboard_content'))
    else:
        form = PdfMenuForm(site=request.site, instance=instance)
    return direct_to_template(request, template='dashboard/content/pdf_form.html', extra_context={
        'form': form
    })

@login_required
def delete_pdf(request, pdf_id):
    return delete_site_object(request, PdfMenu, pdf_id, 'dashboard_content')

@login_required
def preview_pdf(request, pdf_id):
    pdf = PdfMenu.objects.get(id=pdf_id)
    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = 'filename=menu-preview.pdf'
    response.write(pdf.render())
    return response

@login_required
def feature_pdf(request, pdf_id):
    pdf = PdfMenu.objects.get(id=pdf_id)
    pdf.featured = True
    pdf.save()
    PdfMenu.objects.exclude(id=pdf_id).update(featured=False)
    messages.success(request, '"%s" has been added to your home page.' % pdf.name)
    return HttpResponseRedirect(reverse('dashboard_content'))

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
        'dashboard/content/img_form.html', 'dashboard_content')

@login_required
def edit_img(request, img_id):
    return add_edit_site_object(request, ItemImage, EditImageForm, 
        'dashboard/content/img_form.html', 'dashboard_content', object_id=img_id)

@login_required
def delete_img(request, img_id):
    return delete_site_object(request, ItemImage, img_id, 'dashboard_content')

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
