def site(request):
    return {'site': request.site}

def custom_media_url(request):
    return {'CUSTOM_MEDIA_URL': request.site.custom_media_url}
