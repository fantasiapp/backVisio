import email
from django.contrib.auth.models import User
from django.contrib import auth
from mysite import settings
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
import jwt
from .modelStructure.dataDashboard import DataDashboard
from visioServer.models import UserProfile, ParamVisio, LogClient
from django.utils import timezone
import json
import requests

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
        response = requests.get(self.googleUrl, headers={}, params={'access_token':userResponse["authToken"]})
        responseDict = response.json()
        if "error" in responseDict:
            return Response({"error": responseDict["error"]})  
        if responseDict["audience"] != settings.GOOGLE_OAUTH2_CLIENT_ID:
            return Response({"error": "Bad client ID"})
        if responseDict["email"] == userResponse["username"]:
            try:
                user = User.objects.get(email = responseDict["email"])
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                token, created = Token.objects.get_or_create(user=user)
            except User.DoesNotExist:
                return Response({"error": "User not found"})
            return Response({"token": token.key, "username": user.username})
        return Response({"":"Not yet implemented"})

    def get(self, request):
        return Response({"error":"GET query is not allowed"})

class ApiTokenAuthAzure(APIView):
    permission_classes = (AllowAny,)
    azureUrl = "https://login.microsoftonline.com/common/oauth2/v2.0/token"

    def post(self, request):
        def validateToken(token):
            tokenHeader = jwt.get_unverified_header(token)
            publicKey = tokenHeader["kid"]
            print("token :", token)
            print("publicKey :",publicKey)
            # decodedToken = jwt.decode(token, publicKey ,algorithms=["RS256"])
            #Hard coded token
            encodedJWT = '''eyJ0eXAiOiJKV1QiLCJub25jZSI6IkJ1OTAtS1ZsdXBoSHVweHdmNjNPaDY3eWRQSzV5QVlLUWVuODJVNGZkZlUiLCJhbGciOiJSUzI1NiIsIng1dCI6ImpTMVhvMU9XRGpfNTJ2YndHTmd2UU8yVnpNYyIsImtpZCI6ImpTMVhvMU9XRGpfNTJ2YndHTmd2UU8yVnpNYyJ9.eyJhdWQiOiIwMDAwMDAwMy0wMDAwLTAwMDAtYzAwMC0wMDAwMDAwMDAwMDAiLCJpc3MiOiJodHRwczovL3N0cy53aW5kb3dzLm5ldC9mNjU4ZWVjOC1lNjA1LTQ0NjMtYjQ5OC1iNzEwZWRjZjRkZjMvIiwiaWF0IjoxNjUyMTkzNzczLCJuYmYiOjE2NTIxOTM3NzMsImV4cCI6MTY1MjE5ODM0MCwiYWNjdCI6MCwiYWNyIjoiMSIsImFpbyI6IkFVUUF1LzhUQUFBQUpwMDlMVHVwU3JNMTZhOHdqVS9vQzlKR0pNRHZsaTFjYUZCL2FQblJZZDB2QWxGRis0SEtTajJhWi9uNzhvLzk5aEVTTWoraWJ0RnVEVFNrMWtSbnpRPT0iLCJhbHRzZWNpZCI6IjE6bGl2ZS5jb206MDAwNjdGRkVCM0EwOEY3MyIsImFtciI6WyJwd2QiXSwiYXBwX2Rpc3BsYXluYW1lIjoidmlzaW9GYW50YXNpYXBwIiwiYXBwaWQiOiJiMDkxZmVmZi1kZGQ4LTQ0ZTAtODgwNS1lNTNhYjNmZDExOTgiLCJhcHBpZGFjciI6IjAiLCJlbWFpbCI6IndpbGxpYW1sb3JnZXJlQGhvdG1haWwuZnIiLCJmYW1pbHlfbmFtZSI6IkwiLCJnaXZlbl9uYW1lIjoid2lsbGlhbSIsImlkcCI6ImxpdmUuY29tIiwiaWR0eXAiOiJ1c2VyIiwiaXBhZGRyIjoiODAuMTIuODEuMTY1IiwibmFtZSI6IndpbGxpYW0gTCIsIm9pZCI6IjQwZjQ3ZmZkLTgzNzYtNDViOC04N2E3LTI3MGQ2ZDExZjk3NSIsInBsYXRmIjoiNSIsInB1aWQiOiIxMDAzMjAwMUY4NjFDNUNCIiwicmgiOiIwLkFYa0F5TzVZOWdYbVkwUzBtTGNRN2M5Tjh3TUFBQUFBQUFBQXdBQUFBQUFBQUFDVUFDTS4iLCJzY3AiOiJvcGVuaWQgcHJvZmlsZSBlbWFpbCIsInN1YiI6ImZQc3RGNENKT2U3akVZVlhnTzRDVzl2RXBiSjdtODZ5ZW0tSWw2VlRFYlEiLCJ0ZW5hbnRfcmVnaW9uX3Njb3BlIjoiRVUiLCJ0aWQiOiJmNjU4ZWVjOC1lNjA1LTQ0NjMtYjQ5OC1iNzEwZWRjZjRkZjMiLCJ1bmlxdWVfbmFtZSI6ImxpdmUuY29tI3dpbGxpYW1sb3JnZXJlQGhvdG1haWwuZnIiLCJ1dGkiOiJpaldWa1BhU3lFcVFNRDRBNDJlZ0FBIiwidmVyIjoiMS4wIiwid2lkcyI6WyI2MmU5MDM5NC02OWY1LTQyMzctOTE5MC0wMTIxNzcxNDVlMTAiLCJiNzlmYmY0ZC0zZWY5LTQ2ODktODE0My03NmIxOTRlODU1MDkiXSwieG1zX3N0Ijp7InN1YiI6ImVwajdWYzdRQ3NKZVBEcGlKZ1ZBT0NVbnlyNEczMkl3M0V4TlJYWVBMaGMifSwieG1zX3RjZHQiOjE2NTIwOTAzNjN9.box-hwGb3kqJVDyVVBVmJ6sfKqvYfrmogGwQ1XZkfDnzMdCphf6DzU6fSi7x4BsbplmjeAS_3aFwKHzDC2zXyxVMPJHNhUKtMLIhWeBq08kCDdv4_L9TG_mOMw7gIHzXBXJ7Kb1Ha1szL4TWdjo0Ep12D_wq9wngliTIqly93xJfBMm4NUGCZo_7TIImRwzlkUgQ48HzFU3HuFk9-dRQLDC37si0lo0QnAbg9z6_iIU4a1ZZa3di9Qo1ZXqiU4m6gicZFU8zgW9m5KaMq5xDhsgKQ4g4uyEuGKZ1pNIcUEnKAUsmh4sFKH6qp5cr4b54XYcZD6HuUmK2pc3Q1hMPYw'''
            publicKey = '''-----BEGIN PUBLIC KEY-----
            jS1Xo1OWDj_52vbwGNgvQO2VzMc
            -----END PUBLIC KEY-----'''
            decodedToken = jwt.decode(encodedJWT, publicKey, algorithms=['RS256'])
            print("decodedToken", decodedToken)
            return False
        
        jsonBin = request.body
        jsonString = jsonBin.decode("utf8")
        userResponse = json.loads(jsonString)
        if not validateToken(userResponse["authToken"]):
            return Response({"error": "Bad token"})
        return Response({"token": "token", "username": "username"})
