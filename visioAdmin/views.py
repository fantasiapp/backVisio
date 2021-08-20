from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib import auth

def home(request):
  if request.user.is_authenticated:
    return redirect('/visio/performances/')
  return redirect('/visio/login/')

def performances(request):
    return 'foo'

def login(request):
    return 'bar'
