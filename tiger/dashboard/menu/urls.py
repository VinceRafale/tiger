from django.conf.urls.defaults import *


urlpatterns = patterns('tiger.dashboard.menu.views',
    url(r'^$', 'section_list', name='dashboard_menu'),
    url(r'^sections/add/$', 'add_edit_section', name='dashboard_add_section'),
    url(r'^sections/delete/(\d+)/$', 'delete_section', name='dashboard_delete_section'),
    url(r'^sections/edit/(\d+)/$', 'add_edit_section', name='dashboard_edit_section'),
    url(r'^sections/edit/(\d+)/price-points/$', 'edit_section_pricepoints', name='edit_section_pricepoints'),
    url(r'^sections/edit/(\d+)/sides/$', 'edit_section_sides', name='edit_section_sides'),
    url(r'^sections/edit/(\d+)/extras/$', 'edit_section_extras', name='edit_section_extras'),
    url(r'^sections/view/(\d+)/$', 'view_section', name='dashboard_view_section'),
    url(r'^sections/reorder/$', 'reorder_sections', name='dashboard_reorder_sections'),
    url(r'^items/add/$', 'add_edit_item', name='dashboard_add_item'),
    url(r'^items/delete/(\d+)/$', 'delete_item', name='dashboard_delete_item'),
    url(r'^items/edit/(\d+)/$', 'add_edit_item', name='dashboard_edit_item'),
    url(r'^items/reorder/$', 'reorder_items', name='dashboard_reorder_item'),
    url(r'^items/flag/$', 'flag_item', name='dashboard_flag_item'),
)


