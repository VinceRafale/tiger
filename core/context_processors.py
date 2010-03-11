from tiger.search.forms import MenuSearchForm

def cart(request):
    return {
        'cart': getattr(request, 'cart', ''),
        'search_form': MenuSearchForm(request.GET)
    }
