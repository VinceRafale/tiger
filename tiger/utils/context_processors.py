from tiger.search.forms import MenuSearchForm

def mobile(request):
    if request.is_mobile:
        font_data = request.site.font_data()
        menu_json = request.site.menu_json()
        context = {
            'font_key': font_data['md5'],
            'menu_key': menu_json['md5']
        }
        context['fonts_are_cached'] = True if request.COOKIES.get('font_key') == font_data['md5'] else False
        context['menu_is_cached'] = True if request.COOKIES.get('menu_key') == menu_json['md5'] else False
        return context
    return {}
