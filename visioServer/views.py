from django.http.response import JsonResponse
from django.shortcuts import render
from django.contrib import auth

def login(request):    
    user = auth.authenticate(
        username = request.POST.get('userName'),
        password = request.POST.get('password')
    )
    if user is not None:
        return JsonResponse("Success")
    return JsonResponse("Failure")