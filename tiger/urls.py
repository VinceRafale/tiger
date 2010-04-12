from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

handler404 = 'tiger.utils.views.handler404'
handler500 = 'tiger.utils.views.handler500'

urlpatterns = patterns('django.views.generic.simple',
    url(r'^$', 'direct_to_template', {'template': 'base.html'}, name='home'),
    url(r'^about/$', 'direct_to_template', {'template': 'about.html'}, name='home'),
    url(r'^find-us/$', 'direct_to_template', {'template': 'find-us.html'}, name='home'),
)

order_patterns = patterns('tiger.core.views',
    url(r'^$', 'preview_order', name='preview_order'),
    url(r'^remove/$', 'remove_item', name='remove_item'),
    url(r'^send/$', 'send_order', name='send_order'),
    url(r'^success/$', 'order_success', name='order_success'),
)

urlpatterns += patterns('',
    (r'^dashboard/', include('tiger.dashboard.urls')),
    (r'^menu/', include('tiger.core.urls')),
    (r'^order/', include(order_patterns)),
    url(r'^m/(?P<item_id>\w+)/$', 'tiger.core.views.short_code', name='short_code'),
    (r'^images/', include('tiger.content.urls')),
    url(r'^search/', 'tiger.search.views.search', name='menu_search'),
    (r'^admin/', include(admin.site.urls)),
    url(r'^join/$', 'tiger.core.views.mailing_list_signup', name='mailing_list_signup'),
    url(r'^s/', include('tiger.look.urls')),
    url(r'^sitemap.xml$', 'tiger.sitemaps.sitemap'),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT}),
)
