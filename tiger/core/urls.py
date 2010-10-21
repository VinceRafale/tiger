from django.conf.urls.defaults import *

urlpatterns = patterns('tiger.core.views',
    url(r'^$', 'section_list', name='menu_home'),
    url(r'^(?P<section_id>\d+)/(?P<section_slug>[\w-]+)/$', 'section_detail', name='menu_section'),
    url(r'^(?P<section_id>\d+)/(?P<section_slug>[\w-]+)/(?P<item_id>\d+)/(?P<item_slug>[\w-]+)/$', 'item_detail', name='menu_item'),
    url(r'^(?P<section_id>\d+)/(?P<section_slug>[\w-]+)/(?P<item_id>\d+)/(?P<item_slug>[\w-]+)/order/$', 'order_item', name='order_item'),
    url(r'^(?P<section>[\w-]+)/$', 'section_detail_abbr', name='menu_section_abbr'),
    url(r'^(?P<section>[\w-]+)/(?P<item>[\w-]+)/$', 'item_detail_abbr', name='menu_item_abbr'),
)
