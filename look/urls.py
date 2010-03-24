from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^(?P<skin_id>\d+)-(?P<timestamp>\d+).css$', 'tiger.look.views.render_skin', name='render_skin'),
)
