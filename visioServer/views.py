import email
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from .modelStructure.dataDashboard import DataDashboard
from visioServer.models import UserProfile, ParamVisio, LogClient
from django.utils import timezone
import json
import requests
from django.contrib.auth.models import User

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
            #request.META['SERVER_PORT'] == '8000' check if server is local
            dataDashBoard = DataDashboard(currentProfile[0], userIdGeo, userGroup[0], request.META['SERVER_PORT'] == '8000')
            if not getattr(dataDashBoard, "__pdvs", False) or not getattr(dataDashBoard, "__pdvs_ly", False):
                return Response({"warning":"inititialisation in progress"})
            action = request.GET["action"]
            if action == "dashboard":
                print("login",currentUser.username)
                LogClient.objects.create(date=timezone.now(), referentielVersion=ParamVisio.getValue("referentielVersion"), softwareVersion=ParamVisio.getValue("softwareVersion"), user=currentUser, path=json.dumps("login"), mapFilters=json.dumps("login"))
                
                return Response(dataDashBoard.dataQuery)
            elif action == "update":
                print(f"get {currentUser} {action}", request.GET["nature"])
                answer = dataDashBoard.getUpdate(request.GET["nature"])
                return Response(answer)
            return Response({"error":f"action {action} unknown"}, headers={'Content-Type':'application/json', 'Content-Encoding': 'gzip'})
        return Response({"error":f"no action defined"})

    def post(self, request):
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
            if not getattr(dataDashBoard, "__pdvs", False) or not getattr(dataDashBoard, "__pdvs_ly", False):
                return Response({"error":"initiialisation in progress"})
            return Response(dataDashBoard.postUpdate(currentUser, jsonString))
        return Response({"error":"empty body"})

class ApiTokenAuthGoogle(APIView):
    permission_classes = (AllowAny,)
    googleUrl = "https://www.googleapis.com/oauth2/v1/tokeninfo/"

    def post(self, request):
        jsonBin = request.body
        jsonString = jsonBin.decode("utf8")
        userResponse = json.loads(jsonString)
        print("post ApiTokenAuthGoogle", jsonString)
        response = requests.get(self.googleUrl, headers={}, params={'access_token':userResponse["authToken"]})
        print("google response: ", response.text)
        responseDict = response.json()
        if "error" in responseDict:
            return Response({"error":responseDict["error"]})   
        if responseDict["email"] == userResponse["username"]:
            print("same email")
            user = User.objects.get(email = responseDict["email"])
            print("user", user)
            print(type(user))
            user = UserProfile({"email": responseDict["email"]})
            print("user2", user)
        return Response({"error":"Not yet implemented"})

    def get(self, request):
        return Response({"error":"GET query is not allowed"})