from django.conf.urls.defaults import *


urlpatterns = patterns('tiger.dashboard.content.views',
    url(r'^$', 'home', name='dashboard_content'),
    url(r'^pdf/add/$', 'add_edit_pdf', name='dashboard_add_pdf'),
    url(r'^pdf/delete/(\d+)/$', 'delete_pdf', name='dashboard_delete_pdf'),
    url(r'^pdf/edit/(\d+)/$', 'add_edit_pdf', name='dashboard_edit_pdf'),
    url(r'^pdf/preview/(\d+)/$', 'preview_pdf', name='dashboard_preview_pdf'),
)


