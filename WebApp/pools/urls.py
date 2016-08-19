# encoding: utf-8
from django.conf.urls import include, url
from . import views

#urlpatterns = patterns('',
#    url(r'^$', views.post_list),
#    url(r'^post/new/$', views.post_new, name='post_new'),
#)
import os

PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))

MEDIA_ROOT = os.path.join(PROJECT_PATH, 'media')
MEDIA_URL = '/media'

urlpatterns = [
#    ('^_ah/warmup$', 'djangoappengine.views.warmup'),
    url(r'^$', views.index),
    url(r'^status/$', views.place_status),
    url(r'^details/$', views.details),
    url(r'^login/$', views.login),
    url(r'^signin/$', views.signin),
    url(r'^check_user/$', views.check_user),
#    ('^tbl_inserts/$', member.views.tbl_inserts),
    url(r'^apply/$', views.apply),
    url(r'^place_manage/$', views.place_manage),
    url(r'^logout/$', views.logout_view),
    url(r'^member/$', include('pools.member.urls')),
    
    #ajax functions
#    ('^get_placeinfo/$','views.get_placeinfo'),
#    ('^chk_timing/$','views.chk_place_ready'),
        
    #for member functions
    
    #for public access..
#    (r'^(?P<path>.*)$', 'django.views.static.serve', {'document_root': MEDIA_ROOT}),
]

