from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .modelStructure.dataDashboard import DataDashboard
from visioServer.models import UserProfile
import json

class DefaultView(APIView):
    permission_classes = (IsAuthenticated,)
    isBlocked = False

class Data(DefaultView):
    def get(self, request):
        if not Data.isBlocked:
            currentUser = request.user
            userGroup = request.user.groups.values_list('name', flat=True)
            currentProfile = UserProfile.objects.filter(user=currentUser)
            if userGroup:
                userIdGeo = currentProfile[0].idGeo if currentProfile else None
            else:
                return Response({"error":f"no profile defined for {currentUser.username} defined"})
            if 'blocked' in request.GET:
                Data.blocked = True
                print("queries are blocked", Data.blocked)
            if 'action' in request.GET:
                #request.META['SERVER_PORT'] == '8000' check if server is local
                dataDashBoard = DataDashboard(currentProfile[0], userIdGeo, userGroup[0], request.META['SERVER_PORT'] == '8000')
                action = request.GET["action"]
                if action == "dashboard":
                    Data.blocked = False
                    print("queries are not blocked", Data.blocked)
                    return Response(dataDashBoard.dataQuery)
                elif action == "update":
                    answer = dataDashBoard.getUpdate(request.GET["nature"])
                    return Response(answer)
                return Response({"error":f"action {action} unknown"}, headers={'Content-Type':'application/json', 'Content-Encoding': 'gzip'})
        else:
            print("data is blocked")
        return Response({"error":f"no action defined"})

    def post(self, request):
        if not Data.isBlocked:
            jsonBin = request.body
            jsonString = jsonBin.decode("utf8")
            currentUser = request.user
            userGroup = request.user.groups.values_list('name', flat=True)
            currentProfile = UserProfile.objects.filter(user=currentUser)
            if userGroup:
                userIdGeo = currentProfile[0].idGeo if currentProfile else None
            else:
                return Response({"error":f"no profile defined for {currentUser.username} defined"})
            if jsonString:
                dataDashBoard = DataDashboard(currentProfile[0], userIdGeo, userGroup[0], request.META['SERVER_PORT'] == '8000')

                return Response(dataDashBoard.postUpdate(currentUser, jsonString))
        else:
            print("data is blocked")
        return Response({"error":"empty body"})