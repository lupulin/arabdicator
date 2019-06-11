'''
Created on Jan 16, 2013

@author: Chris Bartos - me@chrisbartos.com
@file: /Users/topher/Developer/abrcapi/abrcapi/projects/urls.py

'''
from abrcapi.projects.pm.urls import v1_api
from django.conf.urls import patterns, include

urlpatterns = patterns('',
    (r'^v1/', include(v1_api.urls)),
    (r'^', include('abrcapi.projects.pm.urls')),
#    (r'^order/', include('abrcapi.projects.order.urls')),
)
