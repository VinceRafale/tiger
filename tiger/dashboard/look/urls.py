from django.conf.urls.defaults import *

urlpatterns = patterns('tiger.dashboard.look.views',
    url(r'^$', 'picker', name='dashboard_look'),
    url(r'^select-skin/$', 'select_skin', name='select_skin'),
    url(r'^get-font-css/$', 'get_font_css', name='get_font_css'),
    url(r'^get-body-font-css/$', 'get_body_font_css', name='get_body_font_css'),
    url(r'^get-bg-css/$', 'get_bg_css', name='get_bg_css'),
    url(r'^get-custom-bg-css/$', 'get_custom_bg_css', name='get_custom_bg_css'),
    url(r'^set-img/$', 'set_img', name='set_img'),
)

