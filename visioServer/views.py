from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .modelStructure.dataDashboard import DataDashboard
from visioServer.models import UserProfile
import json

class DefaultView(APIView):
    permission_classes = (IsAuthenticated,)

class Data(DefaultView):
    def get(self, request):
        currentUser = request.user
        userGroup = request.user.groups.values_list('name', flat=True)
        currentProfile = UserProfile.objects.filter(user=currentUser)
        if userGroup:
            userIdGeo = currentProfile[0].idGeo if currentProfile else None
        else:
            return Response({"error":f"no profile defined for {currentUser.username} defined"})
        if 'action' in request.GET:
            action = request.GET["action"]
            if action == "dashboard":
                #request.META['SERVER_PORT'] == '8000' check if query is local
                dataDashBoard = DataDashboard(userIdGeo, userGroup[0], request.META['SERVER_PORT'] == '8000')
                return Response(dataDashBoard.dataQuery)
            elif action == "update":
                answer = DataDashboard.getUpdate(userIdGeo, userGroup[0], request.GET["nature"])
                return Response(answer)
            return Response({"error":f"action {action} unknown"}, headers={'Content-Type':'application/json', 'Content-Encoding': 'gzip'})
        return Response({"error":f"no action defined"})

    def post(self, request):
        print("body", request.body)
        currentUser = request.user
        userGroup = request.user.groups.values_list('name', flat=True)
        currentProfile = UserProfile.objects.filter(user=currentUser)
        if userGroup:
            userIdGeo = currentProfile[0].idGeo if currentProfile else None
        print("what data POST", list(request.POST.keys()), list(request.POST.values()))
        if 'action' in request.GET:
            action = request.GET["action"]
            print("who is it?", currentUser, userGroup[0], userIdGeo)
            if action == "update":
                print("what data POST", list(request.POST.keys()), list(request.POST.values()), "GET", list(request.GET.keys()), list(request.GET.values()))
                answer = DataDashboard.postUpdate(userIdGeo, userGroup[0], request.POST)
                return Response(answer)
        return Response({"message":"test"})
            
