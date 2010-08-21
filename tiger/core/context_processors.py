from tiger.search.forms import MenuSearchForm

def cart(request):
    if request.path.startswith('/dashboard'):
        return ''
    return {
        'cart': getattr(request, 'cart', ''),
        'search_form': MenuSearchForm(request.GET)
    }
