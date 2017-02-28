from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^sdp/services/SendSmsToLocation', views.lbs_sdp_service),

]
