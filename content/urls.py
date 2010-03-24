from django.conf.urls.defaults import *

urlpatterns = patterns('tiger.content.views',
    url(r'^(?P<image_id>\d+)/(?P<slug>[\w-]+)/$', 'image_detail', name='image_detail'),
)
