from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    url(r'^$', 'zgevgo.basic.views.index_view', name='index'),
    url(r'^stream/(?P<pk>\d+)/$', 'zgevgo.basic.views.stream_view', name='stream'),
    url(r'^/low_level/$', 'zgevgo.basic.views.low_level_view', name='low-level'),
    url(r'^admin/', include(admin.site.urls)),
)
