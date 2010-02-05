from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('tiger.dashboard.views.menu',
    url(r'^$', 'dashboard', name='dashboard'),
)

urlpatterns += patterns('django.contrib.auth.views',
    url(r'^login/$', 'login', {'template_name': 'dashboard/login.html'}, name='auth_login'),
    url(r'^logout/$', 'logout', {'template_name': 'dashboard/logout.html', 'next_page': '/dashboard/login/'}, name='auth_logout'),
)

menu_patterns = patterns('tiger.dashboard.views.menu',
    url(r'^$', 'section_list', name='dashboard_menu'),
    url(r'^sections/add/$', 'add_edit_section', name='dashboard_add_section'),
    url(r'^sections/delete/(\d+)/$', 'delete_section', name='dashboard_delete_section'),
    url(r'^sections/edit/(\d+)/$', 'add_edit_section', name='dashboard_edit_section'),
    url(r'^sections/view/(\d+)/$', 'view_section', name='dashboard_view_section'),
    url(r'^sections/reorder/$', 'reorder_sections', name='dashboard_reorder_sections'),
    url(r'^items/add/$', 'add_edit_item', name='dashboard_add_item'),
    url(r'^items/delete/(\d+)/$', 'delete_item', name='dashboard_delete_item'),
    url(r'^items/edit/(\d+)/$', 'add_edit_item', name='dashboard_edit_item'),
    url(r'^items/reorder/$', 'reorder_items', name='dashboard_reorder_item'),
)

marketing_patterns = patterns('tiger.dashboard.views.marketing',
    url(r'^$', 'home', name='dashboard_marketing'),
    url(r'^blasts/$', 'blast_list', name='dashboard_blast_list'),
    url(r'^blasts/add/$', 'add_edit_blast', name='dashboard_add_blast'),
    url(r'^blasts/delete/(\d+)/$', 'delete_blast', name='dashboard_delete_blast'),
    url(r'^blasts/edit/(\d+)/$', 'add_edit_blast', name='dashboard_edit_blast'),
    url(r'^blasts/preview/(\d+)/$', 'preview_blast', name='dashboard_preview_blast'),
    url(r'^subscribers/$', 'subscriber_list', name='dashboard_subscriber_list'),
    url(r'^subscribers/add/$', 'add_edit_subscriber', name='dashboard_add_subscriber'),
    url(r'^subscribers/delete/(\d+)/$', 'delete_subscriber', name='dashboard_delete_subscriber'),
    url(r'^subscribers/edit/(\d+)/$', 'add_edit_subscriber', name='dashboard_edit_subscriber'),
)

restaurant_patterns = patterns('tiger.dashboard.views.restaurant',
    url(r'^$', 'home', name='dashboard_restaurant'),
    url(r'^location/$', 'location', name='dashboard_location'),
    url(r'^hours/$', direct_to_template, {'template': 'dashboard/hours.html'}, name='mns_editor_settings'),
    url(r'^save-timeslot/$', 'save_timeslot', name='save_timeslot'),
    url(r'^update-timeslot/$', 'update_timeslot', name='update_timeslot'),
    url(r'^delete-timeslot/$', 'delete_timeslot', name='delete_timeslot'),
)

urlpatterns += patterns('',
    (r'^menu/', include(menu_patterns)),
    (r'^marketing/', include(marketing_patterns)),
    (r'^restaurant/', include(restaurant_patterns)),
)
