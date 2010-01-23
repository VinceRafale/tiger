from django.conf import settings
from django.conf.urls.defaults import *

handler404 = 'tiger.utils.views.handler404'
handler500 = 'tiger.utils.views.handler500'

urlpatterns = patterns('',
    url(r'^$', 'django.views.generic.simple.direct_to_template', {'template': 'dashboard.html'}, name='dashboard'),
)

urlpatterns += patterns('tiger.dashboard.views',
    url(r'^menu/$', 'section_list', name='dashboard_menu'),
    url(r'^menu/sections/add/$', 'add_edit_section', name='dashboard_add_section'),
    url(r'^menu/sections/delete/(\d+)/$', 'delete_section', name='dashboard_delete_section'),
    url(r'^menu/sections/edit/(\d+)/$', 'add_edit_section', name='dashboard_edit_section'),
    url(r'^menu/sections/view/(\d+)/$', 'view_section', name='dashboard_view_section'),
    url(r'^menu/sections/reorder/$', 'reorder_sections', name='dashboard_reorder_sections'),
    url(r'^menu/items/add/$', 'add_edit_item', name='dashboard_add_item'),
    url(r'^menu/items/delete/(\d+)/$', 'delete_item', name='dashboard_delete_item'),
    url(r'^menu/items/edit/(\d+)/$', 'add_edit_item', name='dashboard_edit_item'),
    url(r'^menu/items/reorder/$', 'reorder_items', name='dashboard_reorder_item'),
)
