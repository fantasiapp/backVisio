from django.urls import re_path
from . import views

urlpatterns = [
  re_path('^$', views.home, name='home'),
  re_path(r'performances', views.performances, name='performances'),
  re_path(r'principale', views.main, name='main'),
  re_path(r'login', views.login, name='login'),
]
