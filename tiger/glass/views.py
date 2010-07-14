from django.views.generic.date_based import archive_month
from django.views.generic.list_detail import object_list, object_detail

from tiger.glass.models import Post

def get_archives():
    return {'archives': Post.objects.dates('date_posted', 'month', 'DESC')}


def post_list(request):
    return object_list(request, Post.objects.order_by('-date_posted'), 
        extra_context=get_archives())


def post_detail(request, slug, post_id):
    return object_detail(request, Post.objects.filter(slug=slug), 
        object_id=post_id, extra_context=get_archives())


def month_archive(request, year, month):
    return archive_month(request, year=year, month=month, date_field='date_posted',
        queryset=Post.objects.all(), extra_context=get_archives())
