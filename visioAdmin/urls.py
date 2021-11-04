from django.conf.urls import url
from . import views

urlpatterns = [
  url('^$', views.home, name='home'),
  url(r'performances', views.performances, name='performances'),
  url(r'principale', views.main, name='main'),
  url(r'login', views.login, name='login'),
]
