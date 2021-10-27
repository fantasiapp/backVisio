from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib import auth
from django.http import JsonResponse
from .dataModel.manageFromOldDatabase import manageFromOldDatabase
from .admin.adminParam import AdminParam
import sys
sys.path.append('..')
from visioServer.models import UserProfile
from visioServer.modelStructure.dataDashboard import DataDashboard


def home(request):
  print('home:', request.user.is_authenticated)
  if request.user.is_authenticated:
    return redirect('/visioAdmin/performances/')
  return redirect('/visioAdmin/login/')

def performances(request):
  if request.method == 'GET' and 'action' in request.GET:
    if request.GET['action'] == 'disconnect':
      auth.logout(request)
      return redirect('/visioAdmin/login/') 
    dataDashboard = createDataDashBoard(request)
    if isinstance(dataDashboard, dict):
      return JsonResponse(dataDashboard)
    adminParam = AdminParam(dataDashboard) 
    return JsonResponse(performancesAction(request.GET['action'], request.GET, adminParam))
  elif request.method == 'POST' and request.POST.get('login') == "Se connecter":
    HtlmPage = performancesLogin(request)
    if HtlmPage: return HtlmPage
  if request.user.is_authenticated:  
    return render(request, 'visioAdmin/performances.html', {})

def performancesLogin(request):
  userName = request.POST.get('userName')
  password = request.POST.get('password')
  user = auth.authenticate(username=userName, password=password)
  if user == None:
    context = {'userName': userName, 'password':password, 'message':"Le couple login password n'est pas conforme"}
    return render(request, 'visioAdmin/login.html', context)
  else:
    context = {"userName":'', 'password':''}
    auth.login(request, user)

def performancesAction(action, get, adminParam):
  if action == "perfEmptyBase":
    return manageFromOldDatabase.emptyDatabase(get['start'] == 'true')
  elif action == "perfPopulateBase":
    if get['method'] == 'empty':
      return manageFromOldDatabase.emptyDatabase(get['start'] == 'true')
    else:
      return manageFromOldDatabase.populateDatabase(get['start'] == 'true', method=get['method'])
  elif action == "perfImportPdv":
    print("visualize pdv")
    return adminParam.vizualizePdv()
  elif action == "openAd":
    return adminParam.openAd()
  elif action == "test":
    return manageFromOldDatabase.test()
  else:
    return {'titles':[], 'values':[], 'tableIndex':[]}

def login(request):
  if request.method == 'GET':
    print('loginGet', request.GET)
  return render(request, 'visioAdmin/login.html')

def createDataDashBoard(request):
  currentUser = request.user
  userGroup = request.user.groups.values_list('name', flat=True)
  currentProfile = UserProfile.objects.filter(user=currentUser)
  if userGroup:
      userIdGeo = currentProfile[0].idGeo if currentProfile else None
  else:
      return {"error":f"no profile defined for {currentUser.username}"}
  return DataDashboard(currentProfile[0], userIdGeo, userGroup[0], request.META['SERVER_PORT'] == '8000')
