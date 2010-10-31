def site(request):
    return {
        'site': getattr(request, 'site', None),
        'location': getattr(request, 'location', None),
    }

def custom_media_url(request):
    return {'CUSTOM_MEDIA_URL': request.site.custom_media_url}
