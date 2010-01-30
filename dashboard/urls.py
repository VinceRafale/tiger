from django.conf import settings
from django.conf.urls.defaults import *

handler404 = 'tiger.utils.views.handler404'
handler500 = 'tiger.utils.views.handler500'

urlpatterns = patterns('',
)

urlpatterns += patterns('django.contrib.auth.views',
    url(r'^login/$', 'login', {'template_name': 'dashboard/login.html'}, name='auth_login'),
    url(r'^logout/$', 'logout', {'template_name': 'dashboard/logout.html', 'next_page': '/dashboard/login/'}, name='auth_logout'),
)

urlpatterns += patterns('tiger.dashboard.views.menu',
    url(r'^$', 'dashboard', name='dashboard'),
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

urlpatterns += patterns('tiger.dashboard.views.marketing',
    url(r'^marketing/$', 'home', name='dashboard_marketing'),
    url(r'^marketing/blasts/$', 'blast_list', name='dashboard_blast_list'),
    url(r'^marketing/blasts/add/$', 'add_edit_blast', name='dashboard_add_blast'),
    url(r'^marketing/blasts/delete/(\d+)/$', 'delete_blast', name='dashboard_delete_blast'),
    url(r'^marketing/blasts/edit/(\d+)/$', 'add_edit_blast', name='dashboard_edit_blast'),
    url(r'^marketing/blasts/preview/(\d+)/$', 'preview_blast', name='dashboard_preview_blast'),
    url(r'^marketing/subscribers/$', 'subscriber_list', name='dashboard_subscriber_list'),
    url(r'^marketing/subscribers/add/$', 'add_edit_subscriber', name='dashboard_add_subscriber'),
    url(r'^marketing/subscribers/delete/(\d+)/$', 'delete_subscriber', name='dashboard_delete_subscriber'),
    url(r'^marketing/subscribers/edit/(\d+)/$', 'add_edit_subscriber', name='dashboard_edit_subscriber'),
)
