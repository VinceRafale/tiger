import json

from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.simple import direct_to_template

from tiger.look.forms import *
from tiger.look.models import Skin

def picker(request):
    form = SkinSelectForm()
    font_form = HeaderFontForm()
    body_font_form = BodyFontForm()
    bg_form = BackgroundForm()
    bg_color_form = BackgroundColorForm()
    bg_img_form = BackgroundImageForm()
    custom_bg_form = CustomBackgroundForm()
    return direct_to_template(request, template='dashboard/look/preview.html',
        extra_context={
            'header_font_form': font_form,
            'body_font_form': body_font_form,
            'bg_form': bg_form,
            'custom_bg_form': custom_bg_form,
            'bg_color_form': bg_color_form,
            'bg_img_form': bg_img_form,
    })


def get_font_css(request):
    font = FontFace.objects.get(id=request.POST.get('font'))
    return HttpResponse(font.as_css())

def get_body_font_css(request):
    form = BodyFontForm(request.POST)
    form.full_clean()
    return HttpResponse(form.cleaned_data['body_font'])

def get_bg_css(request):
    bg = Background.objects.get(id=request.POST.get('bg'))
    return HttpResponse(bg.as_css())

def get_custom_bg_css(request):
    form = CustomBackgroundForm(request.POST, instance=request.site.background)
    form.full_clean()
    print form._errors
    bg = form.save(commit=False)
    return HttpResponse(bg.as_css())

def set_img(request):
    form = BackgroundImageForm(request.POST, request.FILES, instance=request.site.background)
    form.full_clean()
    bg = form.save()
    data = {
        'selector': '#background',
        'css': 'body { %s }' % bg.as_css()
    }
    return HttpResponse(json.dumps(data))

def select_skin(request):
    skin_id = request.POST.get('id')
    skin = Skin.objects.get(id=skin_id)
    site = request.site
    site.skin = skin
    site.save()
    return HttpResponse("Your settings have been saved.")
