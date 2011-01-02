from django.conf.urls.defaults import *

urlpatterns = patterns('tiger.stork.views',
    url(r'^main.js$', 'script_tag', name='stork_script'),
    url(r'^font/((?:\w+-)+\w+).css$', 'font_css', name='font_css'),
    url(r'^font/((?:\w+-)+\w+)~(\d+).css$', 'font_css', name='font_css_with_selection'),
    url(r'^image/([\w-]+)/get/$', 'image_css', name='image_css'),
    url(r'^image/([\w-]+)/$', 'stage_image', name='stage_image'),
    url(r'^image/([\w-]+)/remove/$', 'remove_image', name='remove_image'),
    url(r'^save/$', 'save', {'redirect_to': 'dashboard_content'}, name='save'),
    url(r'^html/([\w-]+)/preview/$', 'preview_html', name='preview_html'),
    url(r'^html/([\w-]+)/revert/$', 'revert_html', name='revert_html'),
)
