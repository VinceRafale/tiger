from haystack.query import SearchQuerySet

from tiger.search.forms import MenuSearchForm
from tiger.utils.views import render_custom

def search(request):
    sqs = SearchQuerySet().filter(site=request.site.id)
    query = ''
    results = []
    if request.META.has_key('QUERY_STRING'):
        form = MenuSearchForm(request.GET, searchqueryset=sqs, load_all=True)
        if form.is_valid():
            query = form.cleaned_data['q']
            results = form.search()
    else:
        form = MenuSearchForm(searchqueryset=sqs, load_all=True)
    context = {
        'results': results,
        'query': query,
    }
    return render_custom(request, 'search/search.html', context)
