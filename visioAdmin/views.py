from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib import auth
from django.http import JsonResponse
from django import forms
from django.contrib.auth.models import User
from .dataModel.manageFromOldDatabase import manageFromOldDatabase
from .admin.adminParam import AdminParam
from .admin.adminUpdate import AdminUpdate
from .admin.adminConsult import AdminConsult
import sys
import os
sys.path.append('..')
from visioServer.models import *
from visioServer.modelStructure.dataDashboard import DataDashboard
from .dataModel import principale


def home(request):
  if isAuthenticated(request):
    return redirect('/visioAdmin/principale/')
  return redirect('/visioAdmin/login/')

def main(request):
  print("view main", isAuthenticated(request))
  if isAuthenticated(request):
    if request.method == "POST":
      return mainActionPost(request)
    if 'action' in request.GET:
      response = mainActionGet(request)
      return JsonResponse(response) if isinstance(response, dict) else response
    return render(request, 'visioAdmin/principale.html', {})
  return redirect('/visioAdmin/login/')

def isAuthenticated(request):
  if request.user.is_authenticated:
    currentUser = request.user
    currentProfile = UserProfile.objects.filter(user=currentUser)
    if currentProfile:
      admin = currentProfile[0].admin
      if admin:
        logAdmin(request, currentUser)
        return True
  return False

def logAdmin(request, currentUser):
  date = timezone.now()
  currentVersion = DataAdmin.objects.get(currentBase=True).getVersion
  savedVersion = DataAdmin.objects.get(currentBase=False).getVersion
  action , param = None, None
  if request.method == "GET":
    if "action" in request.GET and not request.GET["action"] in ["paramSynonymsInit", "setupCreateAccount", "buildTarget", "buildValidate", "createTable", "visualizeTargetTable", "visualizeActionTable", "paramAccountInit"]:
      action = request.GET["action"]
  elif request.POST.get('uploadFile'):
    action = f"upoladFile {request.POST.get('uploadFile')}"
    param = request.FILES['file']
  elif request.POST.get('login'): action = 'login'
  elif request.POST.get('action') and request.POST.get('action') == 'disconnect': action = 'disconnect'
  elif request.POST.get('defineSynonym'): action = 'defineSynonym'
  elif request.POST.get('modifyTarget'): action = 'modifyTargetLevel'
  elif request.POST.get('updateValidate'): action = 'updateTargetRef'
  elif request.POST.get('activateCreationAccount'):
    action = 'createAccount'
    dictData = json.loads(request.POST.get('dictCreate'))
    param = f'pseudo : {dictData["pseudo"]}, profile : {dictData["profile"]}'
  if action:
    LogAdmin.objects.create(user=currentUser, date=date, currentVersion=currentVersion, savedVersion=savedVersion, method=request.method, action=action, param=param)

def mainActionPost(request):
  dataDashboard = createDataDashBoard(request)
  adminParam = AdminParam(dataDashboard)
  if request.POST.get('uploadFile'):
    response = principale.handleUploadedFile(request.FILES['file'], request.POST.get('uploadFile'))
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
  elif request.POST.get('defineSynonym'): return JsonResponse(adminParam.fillupSynonym(request.POST.get('dictSynonym')))
  elif request.POST.get('activateCreationAccount'): return JsonResponse(adminParam.activateCreationAccount(request.POST.get('dictCreate')))
  elif request.POST.get('modifyTarget'): return JsonResponse(adminParam.modifyTarget(request.POST.get('dictTarget')))
  elif request.POST.get('updateValidate'): return JsonResponse(adminParam.updateValidate(request.POST.get('dictValidate')))
  

def mainActionGet(request):
  print("mainActionGet", request.GET["action"])
  if request.GET["action"] == "loadInit": return principale.loadInit()
  dataDashboard = createDataDashBoard(request)
  adminParam = AdminParam(dataDashboard)
  adminUpdate = AdminUpdate(dataDashboard)
  adminConsult = AdminConsult(adminUpdate, adminParam)
  # update Ref
  if request.GET["action"] == "selectAgent": return adminUpdate.updateRefWithAgent(dict(request.GET))
  elif request.GET["action"] == "switchBase":
    adminUpdate.switchBase()
    dataDashboard = createDataDashBoard(request, delJson=True)
    return principale.loadInit()
  elif request.GET["action"] == "visualizeTable": return adminUpdate.visualizeTable(request.GET["kpi"], request.GET["table"])
  #param
  elif request.GET["action"] == "paramSynonymsInit": return adminParam.paramSynonymsInit()
  elif request.GET["action"] == "switchAdStatus": return adminParam.switchAdStatus()
  elif request.GET["action"] == "paramAccountInit": return adminParam.paramAccountInit()
  elif request.GET["action"] == "setupCreateAccount": return adminParam.setupCreateAccount()
  elif request.GET["action"] == "removeAccount": return adminParam.removeAccount(int(request.GET["id"]))
  elif request.GET["action"] == "modifyAccount": return adminParam.modifyAccount(int(request.GET["id"]), request.GET["name"])
  elif request.GET["action"] == "modifyAgent": return adminParam.modifyAgent(int(request.GET["id"]), request.GET["name"])
  elif request.GET["action"] == "buildTarget": return adminParam.buildTarget()
  elif request.GET["action"] == "buildValidate": return adminParam.buildValidate()
  #consult
  elif request.GET["action"] == "createTable": return adminConsult.buildExcelFile(request.GET["nature"])
  elif request.GET["action"] == "visualizeTargetTable": return adminConsult.visualizeTargetTable(request.GET["table"])
  elif request.GET["action"] == "visualizeActionTable": return adminConsult.visualizeActionTable()

  elif request.GET["action"] == "paramSynonymsInit": return adminParam.paramSynonymsInit()
  return {"info":"Not yet implemented"}

def login(request):
  print("login start", request.method, request.POST.get('login'))
  if request.method == 'POST' and request.POST.get('login') == "Se connecter":
    userName = request.POST.get('userName')
    password = request.POST.get('password')
    print("login userName, password", userName, password, request)
    user = auth.authenticate(username=userName, password=password)
    print("login user", user)
    if user == None:
      context = {'userName':userName, 'message':"Le couple login password n'est pas conforme."}
      return render(request, 'visioAdmin/login.html', context)
    auth.login(request, user)
    print("isAuthenticated", auth.login(request, user), isAuthenticated(request.user), "user", request.user)
    return redirect('principale.html')
  if request.method == 'POST' and request.POST.get('action') == "disconnect":
    currentUser = request.user
    logAdmin(request, currentUser)
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

