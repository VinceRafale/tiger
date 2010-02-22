from models import Skin


def skin(request):
    s = Skin.objects.all()[0]
    print s
    return {'SKIN_URL': s.get_absolute_url()}
