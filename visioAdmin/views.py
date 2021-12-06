from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib import auth
from django.http import JsonResponse
from django import forms
from django.contrib.auth.models import User
from .dataModel.manageFromOldDatabase import manageFromOldDatabase
from .admin.adminParam import AdminParam
from .admin.adminUpdate import AdminUpdate
import sys
import os
sys.path.append('..')
from visioServer.models import *
from visioServer.modelStructure.dataDashboard import DataDashboard
from .dataModel import principale


def home(request):
  if request.user.is_authenticated:
    return redirect('/visioAdmin/principale/')
  return redirect('/visioAdmin/login/')

def main(request):
  if request.user.is_authenticated:
    if request.method == "POST":
      return mainActionPost(request)
    if 'action' in request.GET:
      return JsonResponse(mainActionGet(request))
    return render(request, 'visioAdmin/principale.html', {})
  return redirect('/visioAdmin/login/')

def mainActionPost(request):
  if request.POST.get('uploadFile'):
    response = principale.handleUploadedFile(request.FILES['file'], request.POST.get('uploadFile'))
    dataDashboard = createDataDashBoard(request)
    adminUpdate = AdminUpdate(dataDashboard) 
    if response:
      AdminUpdate.response = response
      updateResponse = adminUpdate.updateFile(request.POST.get('uploadFile'))
      if adminUpdate.getErrors:
        return JsonResponse(adminUpdate.getErrors)
      if updateResponse:
        return JsonResponse(updateResponse)
      return JsonResponse(response)
    return JsonResponse({"error":True, "title":"Erreur", "content":"Le fichier n'a pas été chargé."})
  if request.POST.get('defineSynonym'):
    dataDashboard = createDataDashBoard(request)
    adminParam = AdminParam(dataDashboard)
    return JsonResponse(adminParam.fillupSynonym(request.POST.get('dictSynonym')))



def mainActionGet(request):
  print("mainActionGet", request.GET["action"])
  if request.GET["action"] == "loadInit": return principale.loadInit()
  dataDashboard = createDataDashBoard(request)
  adminParam = AdminParam(dataDashboard)
  adminUpdate = AdminUpdate(dataDashboard)
  # update Ref
  if request.GET["action"] == "selectAgent": return adminUpdate.updateRefWithAgent(dict(request.GET))
  elif request.GET["action"] == "switchBase":
    adminUpdate.switchBase()
    dataDashboard = createDataDashBoard(request, delJson=True)
    return principale.loadInit()
  elif request.GET["action"] == "visualizeTable": return adminUpdate.visualizeTable(request.GET["kpi"], request.GET["table"])
  elif request.GET["action"] == "paramSynonymsInit": return adminParam.paramSynonymsInit()
  elif request.GET["action"] == "paramAccountInit": return adminParam.paramAccountInit()
  elif request.GET["action"] == "switchAdStatus": return adminParam.switchAdStatus()
  return {"info":"Not yet implemented"}

def login(request):
  if request.method == 'POST' and request.POST.get('login') == "Se connecter":
    userName = request.POST.get('userName')
    password = request.POST.get('password')
    user = auth.authenticate(username=userName, password=password)
    if user == None:
      context = {'userName':userName, 'message':"Le couple login password n'est pas conforme."}
      return render(request, 'visioAdmin/login.html', context)
    auth.login(request, user)
    print("login",user.name)
    LogClient.objects.create(date=timezone.now(), referentielVersion=ParamVisio.getValue("referentielVersion"), softwareVersion=ParamVisio.getValue("softwareVersion"), user=user, path=json.dumps("login"))
    return redirect('principale.html')
  if request.method == 'POST' and request.POST.get('action') == "disconnect":
    auth.logout(request)
  return render(request, 'visioAdmin/login.html')

def createDataDashBoard(request, delJson=False):
  currentUser = request.user
  userGroup = currentUser.groups.values_list('name', flat=True)
  currentProfile = UserProfile.objects.filter(user=currentUser)
  if userGroup:
      userIdGeo = currentProfile[0].idGeo if currentProfile else None
  else:
      return {"error":f"no profile defined for {currentUser.username}"}
  if delJson:
    DataDashboard.flagLoad = True
    if request.META['SERVER_PORT'] == '8000':
      os.remove("./visioServer/modelStructure/pdvDict.json")
      os.remove("./visioServer/modelStructure/pdvDict_ly.json")
  return DataDashboard(currentProfile[0], userIdGeo, userGroup[0], request.META['SERVER_PORT'] == '8000')



def performances(request):
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

