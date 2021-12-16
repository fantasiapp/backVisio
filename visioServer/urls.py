from django.urls import include, re_path
from . import views
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
  # url(r'^login', views.login, name='login'),
  re_path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
  re_path('data/', views.Data.as_view(), name='data'),
]