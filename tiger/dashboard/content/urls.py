from django.conf.urls.defaults import *


urlpatterns = patterns('tiger.dashboard.content.views',
    url(r'^$', 'home', name='dashboard_content'),
    url(r'^menu-items$', 'create_menu_item', name='create_menu_item'),
    url(r'^menu-items/(\d+)$', 'delete_menu_item', name='delete_menu_item'),
    url(r'^menu-items/reorder/$', 'reorder_menu_items', name='reorder_menu_items'),
    url(r'^pages/add/$', 'add_edit_page', name='add_page'),
    url(r'^pages/edit/(\d+)/$', 'add_edit_page', name='edit_page'),
    url(r'^pdf/$', 'pdf_list', name='dashboard_pdf_list'),
    url(r'^pdf/add/$', 'add_edit_pdf', name='dashboard_add_pdf'),
    url(r'^pdf/delete/(\d+)/$', 'delete_pdf', name='dashboard_delete_pdf'),
    url(r'^pdf/edit/(\d+)/$', 'add_edit_pdf', name='dashboard_edit_pdf'),
    url(r'^pdf/preview/(\d+)/$', 'preview_pdf', name='dashboard_preview_pdf'),
    url(r'^pdf/feature/$', 'feature_pdf', name='dashboard_feature_pdf'),
    url(r'^img/$', 'img_list', name='dashboard_img_list'),
    url(r'^img/add/$', 'add_img', name='dashboard_add_img'),
    url(r'^img/edit/(\d+)/$', 'edit_img', name='dashboard_edit_img'),
    url(r'^img/delete/(\d+)/$', 'delete_img', name='dashboard_delete_img'),
    url(r'^domain/$', 'custom_domain', name='dashboard_domain'),
    url(r'^get-images/$', 'get_images', name='dashboard_get_images'),
    url(r'^look/docs/$', 'look_docs', name='look_docs'),
    url(r'^google/$', 'google', name='google'),
    url(r'^mobile/$', 'mobile', name='mobile'),
)


