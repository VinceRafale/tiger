from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

from tiger.core.models import Item, Coupon
from tiger.notify.models import Release

handler404 = 'tiger.utils.views.handler404'
handler500 = 'tiger.utils.views.handler500'

urlpatterns = patterns('tiger.utils.views',
    url(r'^$', 'render_custom', {'template': 'base.html'}, name='home'),
    url(r'^robots.txt$', 'robots'),
    url(r'^about/$', 'render_custom', {'template': 'about.html'}, name='about'),
    url(r'^find-us/$', 'render_custom', {'template': 'find-us.html'}, name='find-us'),
)

order_patterns = patterns('tiger.core.views',
    url(r'^$', 'preview_order', name='preview_order'),
    url(r'^remove/$', 'remove_item', name='remove_item'),
    url(r'^send/$', 'send_order', name='send_order'),
    url(r'^success/$', 'order_success', name='order_success'),
    url(r'^pay/p/$', 'payment_paypal', name='payment_paypal'),
    url(r'^pay/p/reg/', include('paypal.standard.ipn.urls')),
    url(r'^add-coupon/$', 'add_coupon', name='add_coupon'),
    url(r'^clear-coupon/$', 'clear_coupon', name='clear_coupon'),
)

if settings.DEBUG:
    order_patterns += patterns('tiger.core.views',
        url(r'^pay/a/$', 'payment_authnet', name='payment_authnet'),
    )
else:
    order_patterns += patterns('tiger.core.views',
        url(r'^pay/a/$', 'payment_authnet', {'SSL': True}, name='payment_authnet'),
    )

urlpatterns += patterns('',
    (r'^dashboard/', include('tiger.dashboard.urls')),
    (r'^menu/', include('tiger.core.urls')),
    (r'^order/', include(order_patterns)),
    (r'^images/', include('tiger.content.urls')),
    url(r'^search/', 'tiger.search.views.search', name='menu_search'),
    url(r'^join/$', 'tiger.core.views.mailing_list_signup', name='mailing_list_signup'),
    url(r'^sitemap.xml$', 'tiger.sitemaps.sitemap'),
)

def qunit(request, path):
    return direct_to_template(request, template='qunit/%s.html' % path)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve',
                {'document_root': settings.MEDIA_ROOT}),
        (r'^qunit/(?P<path>[\w-]+)/$', qunit),
    )


urlpatterns += patterns('tiger.notify.views',
    url(r'^news/$', 'press_list', name='press_list'),
    url(r'^news/(?P<object_id>\d+)/(?P<slug>[\w-]+)/$', 'press_detail', name='press_detail'),
)

urlpatterns += patterns('tiger.utils.views',
    url(r'^m/(?P<item_id>\w+)/$', 'short_code_redirect', {'model': Item}, name='short_code'),
    url(r'^p/(?P<item_id>\w+)/$', 'short_code_redirect', {'model': Release}, name='press_short_code'),
    url(r'^c/(?P<item_id>\w+)/$', 'short_code_redirect', {'model': Coupon}, name='coupon_short_code'),
)
