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
import base64
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicNumbers
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization


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
        def getPublicKey(token):
            kid = jwt.get_unverified_header(token)["kid"]
            publicKeysUrl = settings.AZURE_OAUTH2_PUBLIC_KEYS_URL
            response = requests.get(publicKeysUrl)
            responseDict = response.json()
            for key in responseDict["keys"]:
                if key["kid"] == kid:
                    break
            
    
            # return jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key))

            n = int.from_bytes(base64.urlsafe_b64decode(key["n"].encode('utf-8') + b"=="), "big")
            e = int.from_bytes(base64.urlsafe_b64decode(key["e"].encode('utf-8') + b"=="), "big")
            return RSAPublicNumbers(n = n, e = e).public_key(default_backend()).public_bytes(
                encoding = serialization.Encoding.PEM,
                format = serialization.PublicFormat.SubjectPublicKeyInfo
            )

        def validateToken(token):
            tokenHeader = jwt.get_unverified_header(token)
            kid = tokenHeader["kid"]
            # print("token :", token)
            # print("token type:", type(token))
            # print("publicKey :",publicKey)
            # decodedToken = jwt.decode(token, publicKey ,algorithms=["RS256"])
            
            
            publicKey = getPublicKey(token)

            print("publicKey :",publicKey)
            
            options = {
            'verify_signature': True,
            'verify_exp': True,  
            'verify_nbf': False,
            'verify_iat': False,
            'verify_aud': False  
            }

            decodedToken = jwt.decode(token, 
                                    publicKey,
                                    algorithms=["RS256"],
                                    options = options)

            print("decodedToken", decodedToken)
            if decodedToken:
                return True
            return False
        
        jsonBin = request.body
        jsonString = jsonBin.decode("utf8")
        userResponse = json.loads(jsonString)
        print("userResponse type", type(userResponse))
        print("userResponse", userResponse)
        if not validateToken(userResponse["authToken"]):
            return Response({"error": "Bad token"})
        try:
            user = User.objects.get(email = userResponse["username"])
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            token, created = Token.objects.get_or_create(user=user)
        except User.DoesNotExist:
            return Response({"error": "User not found"})
        return Response({"token": token.key, "username": user.username})
