from django.conf.urls.defaults import *

urlpatterns = patterns('tiger.core.views',
url(r'^$', 'section_list', name='menu_home'),
url(r'^(?P<section>[\w-]+)/$', 'section_detail', name='menu_section'),
url(r'^(?P<section>[\w-]+)/(?P<item>[\w-]+)/$', 'item_detail', name='menu_item'),
)
