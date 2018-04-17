from django.conf.urls import url
from userdata import views

urlpatterns = [
    url(r'^userdata/$', views.userdata_send),
    url(r'^userdata/(?P<userid>[a-zA-Z0-9]+)/$', views.userdata_receive),
    url(r'^cbandit/(?P<userid>[a-zA-Z0-9]+)/$', views.userdata_receive_cbandit),
    url(r'^linreg/(?P<userid>[a-zA-Z0-9]+)/$', views.userdata_receive_linreg),
    url(r'^dnn/(?P<userid>[a-zA-Z0-9]+)/$', views.userdata_receive_dnn),
]