# encoding: utf-8

from django.conf.urls import *

import os

PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))

MEDIA_ROOT = os.path.join(PROJECT_PATH, 'media')

from pools.member.views import *
#from django.conf.urls.defaults import *

from django.contrib.auth.views import *

urlpatterns = [#'member.views',
#    (r'^add_member/$', add_member),
#    url(r'^$', views.index),
    url(r'^$', index),    
    url(r'^message/$', message), 
    url(r'^place_add/$', place_add),        
    url(r'^user_mgm/$', user_mgm),        
    url(r'^user_detail/$', user_detail),        
    url(r'^place_mgm/$', place_mgm), 		#場地管理       
    url(r'^place_detail/$', place_detail),        
    url(r'^place_approve/$', place_approve),  #申請審核        
    url(r'^approve_detail/$', approve_detail),  #場地申請審核細項        
]