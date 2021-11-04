from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib import auth
from django.http import JsonResponse
from django import forms
from django.contrib.auth.models import User
from .dataModel.manageFromOldDatabase import manageFromOldDatabase
from .admin.adminParam import AdminParam
import sys
sys.path.append('..')
from visioServer.models import DataAdmin, UserProfile
from visioServer.modelStructure.dataDashboard import DataDashboard
from django.utils import timezone


def home(request):
  print("home")
  if request.user.is_authenticated:
    return redirect('/visioAdmin/principale/')
  return redirect('/visioAdmin/login/')

def main(request):
  print("main", request.GET, request.method, request.POST.get('uploadFile'))
  if request.user.is_authenticated:
    if request.method == "POST":
      return mainActionPost(request)
    if 'action' in request.GET:
      print("get", request.GET)
      return mainActionGet(request)
    return render(request, 'visioAdmin/principale.html', {})
  print("no authentification")
  return redirect('/visioAdmin/login/')

def mainActionPost(request):
  if request.POST.get('uploadFile'):
    response = handleUploadedFile(request.FILES['file'])
    if response:
      return JsonResponse(response)
    return JsonResponse({"error":"file not saved"})

def handleUploadedFile(fileContent):
  with open(f'visioAdmin/dataFile/Référentiel/{fileContent._get_name()}', 'wb+') as destination:
    for chunk in fileContent.chunks():
      destination.write(chunk)
  dataAdmin = DataAdmin.getLastSavedObject()
  dataAdmin.fileNameRef = fileContent._get_name()
  dataAdmin.dateRef = timezone.now()
  dataAdmin.save()
  return {"status":"OK", "fileName":dataAdmin[0].fileName, "date":dataAdmin[0].date.strftime("%Y-%m-%d %H:%M:%S")}


def mainActionGet(request):
  print("action", request.GET["action"])
  if request.GET["action"] == "updateRef":
    print("mainAction updateRef")
    return JsonResponse({"response":"updateRef"})
  if request.GET["action"] == "loadInit":
    print("mainAction loadInit")
    return JsonResponse({"response":"loadInit"})
  return JsonResponse({"info":None})

def performances(request):
  print("performances")
  if request.method == 'GET' and 'action' in request.GET:
    if request.GET['action'] == 'disconnect':
      auth.logout(request)
      return redirect('/visioAdmin/login/') 
    adminParam =False
    if request.GET['action'] not in ["perfEmptyBase", "perfPopulateBase"]:
      dataDashboard = createDataDashBoard(request)
      if isinstance(dataDashboard, dict):
        return JsonResponse(dataDashboard)
      adminParam = AdminParam(dataDashboard) 
    return JsonResponse(performancesAction(request.GET['action'], request.GET, adminParam))
  if request.user.is_authenticated:  
    return render(request, 'visioAdmin/performances.html', {})

def performancesAction(action, get, adminParam):
  if action == "perfEmptyBase":
    return manageFromOldDatabase.emptyDatabase(get['start'] == 'true')
  elif action == "perfPopulateBase":
    if get['method'] == 'empty':
      return manageFromOldDatabase.emptyDatabase(get['start'] == 'true')
    else:
      return manageFromOldDatabase.populateDatabase(get['start'] == 'true', method=get['method'])
  elif action == "perfImportPdv":
    return adminParam.visualizePdv()
  elif action == "perfImportSales":
    return adminParam.visualizeSales()
  elif action == "perfImportTarget":
    return adminParam.visualizeTarget()
  elif action == "openAd":
    return adminParam.openAd()
  elif action == "test":
    return manageFromOldDatabase.test()
  else:
    return {'titles':[], 'values':[], 'tableIndex':[]}

def login(request):
  print("login")
  if request.method == 'POST' and request.POST.get('login') == "Se connecter":
    userName = request.POST.get('userName')
    password = request.POST.get('password')
    user = auth.authenticate(username=userName, password=password)
    if user == None:
      context = {'userName':userName, 'message':"Le couple login password n'est pas conforme"}
      return render(request, 'visioAdmin/login.html', context)
    auth.login(request, user)
    return redirect('principale.html')
  if request.method == 'POST' and request.POST.get('action') == "disconnect":
    auth.logout(request)
  return render(request, 'visioAdmin/login.html')

def createDataDashBoard(request):
  currentUser = request.user
  userGroup = currentUser.groups.values_list('name', flat=True)
  currentProfile = UserProfile.objects.filter(user=currentUser)
  if userGroup:
      userIdGeo = currentProfile[0].idGeo if currentProfile else None
  else:
      return {"error":f"no profile defined for {currentUser.username}"}
  return DataDashboard(currentProfile[0], userIdGeo, userGroup[0], request.META['SERVER_PORT'] == '8000')
  # return DataDashboard(1, 0, 1, request.META['SERVER_PORT'] == '8000')
