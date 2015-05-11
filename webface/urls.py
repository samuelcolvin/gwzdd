from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    url(r'^$', 'webface.basic.views.index_view', name='index'),
    url(r'^stream/(?P<pk>\d+)/$', 'webface.basic.views.stream_view', name='stream'),
    url(r'^/low_level/$', 'webface.basic.views.low_level_view', name='low-level'),
    url(r'^admin/', include(admin.site.urls)),
)
