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
    url(r'^order/$', 'direct_to_template', {'template': 'core/preview_order.html'}, name='preview_order'),
)
urlpatterns += patterns('',
    (r'^dashboard/', include('tiger.dashboard.urls')),
    (r'^menu/', include('tiger.core.urls')),
    #(r'^search/', include('haystack.urls')),
    (r'^admin/', include(admin.site.urls)),
    url(r'^s/', include('tiger.look.urls')),
    url(r'^order/remove/$', 'tiger.core.views.remove_item', name='remove_item'),
    url(r'^order/send/$', 'tiger.core.views.send_order', name='send_order'),
    url(r'^order/success/$', 'tiger.core.views.order_success', name='order_success'),
    url(r'^m/(?P<item_id>\w+)/$', 'tiger.core.views.short_code', name='short_code'),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT}),
)
