from django.conf.urls import url
from django.urls import path
from . import views
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
  url(r'^login', views.login, name='login'),
  url('api-token-auth/', obtain_auth_token, name='api_token_auth'),
]