from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    url(r'^$', 'zgevgo.basic.views.main_view', name='main_view'),
    url(r'^admin/', include(admin.site.urls)),
)
