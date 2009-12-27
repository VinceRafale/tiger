def site(request):
    
    return {'site': getattr(request, 'site', None)}

def custom_media_url(request):
    return {'CUSTOM_MEDIA_URL': request.site.custom_media_url}
