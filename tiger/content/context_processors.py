from tiger.content.models import MenuItem

def menu_items(request):
    site = request.site
    return {
            'menu_items': MenuItem.objects.filter(site=site)
            }
