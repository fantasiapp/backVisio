from django.http.response import JsonResponse
# from django.shortcuts import render
from django.contrib import auth
from .models import *
import django.apps
from django.forms.models import model_to_dict
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated


# Pas utilisé pour le moment
# def login(request):    
#     user = auth.authenticate(
#         username = request.POST.get('userName'),
#         password = request.POST.get('password')
#     )
#     if user is not None:
#         return JsonResponse("Success")
#     return JsonResponse("Failure")

class DefaultView(APIView):
    permission_classes = (IsAuthenticated,)

class Data(DefaultView):
    def get(self, request):
        data = {}
        for model in django.apps.apps.get_models():
            data.update({model.__name__: [model_to_dict(object) for object in model.objects.all()]})
            if model == Ventes:
                break
        return Response(data)
