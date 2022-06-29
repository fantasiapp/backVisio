from visioServer.models import *
from datetime import datetime, timedelta
import json
import os

class AdminParam:
  fieldNamePdv = False
  fieldNameSales = False

  def __init__(self, dataDashboard):
    self.dataDashboard = dataDashboard
    if not AdminParam.fieldNamePdv:
      AdminParam.titleTarget = json.loads(os.getenv('TITLE_TARGET'))

  # Targets
  def buildTarget(self):
    finition = {agentF.id:{"agentFName":agentF.name, "target":agentF.TargetedNbVisit, "ratio":agentF.ratioTargetedVisit} for agentF in AgentFinitionsSave.objects.filter(currentYear=True)}
    params = {"Coefficient feu tricolore":ParamVisio.getValue("coeffGreenLight"), "Ratio Plaque Enduit":ParamVisio.getValue("ratioPlaqueFinition")}
    return {"Finitions":finition, "Params":params}

  def modifyTarget(self, dictJson):
    dictData = json.loads(dictJson)
    for id, value in dictData["target"].items():
      agentF = AgentFinitionsSave.objects.get(id=id)
      if value.isdigit():
        agentF.TargetedNbVisit = int(value)
        agentF.save()
    for id, value in dictData["ratio"].items():
      agentF = AgentFinitionsSave.objects.get(id=id)
      try:
        agentF.ratioTargetedVisit = float(value)
        agentF.save()
      except:
        pass
    for id, value in dictData["params"].items():
      param = ParamVisio.objects.get(prettyPrint=id)
      if param.field == "Coefficient feu tricolore" and value.isdigit():
        ParamVisio.setValue(param.field, int(value))
      else:
        try:
          ParamVisio.setValue(param.field, float(value))
        except:
          pass
    return {"modifyTarget":"OK"}

  def visualizeTarget(self):
    indexTarget = Pdv.listFields().index("target")
    targets = [self.__editTarget(id, line, line[indexTarget], Pdv.listFields(), Target.listFields()) for id, line in getattr(self.dataDashboard, "__pdvs").items()]
    targets = [target for target in targets if target]
    return {'titles':AdminParam.titleTarget, 'values':targets}

  def __editTarget(self, idPdv, line, target, fieldsPdv, fieldsTarget):
    if target:
      pdv = [line[fieldsPdv.index(field)] for  field in ["code", "name"]]
      targetFormated = [datetime.fromtimestamp(target[fieldsTarget.index("date")]).strftime('%Y-%m-%d')]
      fieldsBool = ['redistributed', 'redistributedFinitions', 'sale']
      targetFormated += ["Non" if target[fieldsTarget.index(field)] else "Oui" for field in fieldsBool]
      targetFormated += ["Oui" if target[fieldsTarget.index("targetFinitions")] else "Non"]
      targetFormated.append('{:,}'.format(target[fieldsTarget.index("targetP2CD")]).replace(',', ' '))
      greenLight = {"g":"Vert", "o":"Orange", "r":"Rouge"}
      targetFormated.append(greenLight[target[fieldsTarget.index("greenLight")]] if target[fieldsTarget.index("greenLight")] else "Aucun")
      targetFormated += [target[fieldsTarget.index(field)] for field in ["bassin", "commentTargetP2CD"]]
      return [f'<button id="Pdv:{idPdv}" class="buttonTarget">OK</button>'] + pdv + targetFormated
    return False

# Account
  def paramAccountInit(self):
    title = {"Nom d'utilisateur":20, "Profil":10, "Secteur":10, "Dernière connexion":12, "Version du référentiel":12, "nombre de connexions":12, "Temps passé":12}
    return {"titles":title, "values":{objUser.id:self.__computeAccountLine(objUser) for objUser in UserProfile.objects.all()}}

  def __computeAccountLine(self, objUser):
    dictProfile = {"agent":Agent, "agentFinitions":AgentFinitions, "drv":Drv}
    user = objUser.user
    group = user.groups.values_list('name', flat=True)[0]
    groupName = dictProfile[group]._meta.verbose_name.title() if group in dictProfile else "Direction Nationale"
    secteur = list(dictProfile[group].objects.filter(id=objUser.idGeo)) if group in dictProfile else "National"
    if isinstance(secteur, list):
      secteur = secteur[0].name if secteur else "Non alloué"
    return [user.username, groupName, secteur] + self.__computeAccountLineOther(user)

  def __computeAccountLineOther(self, user):
    log = LogClient.objects.filter(path=json.dumps("login"), user=user).order_by("-date")
    Other = [str(log[0].date)[:16] if log else "_"]
    Other.append(log[0].referentielVersion if log else "_")
    Other.append(len(log))
    Other.append(self.__computeTimeSpend(user))
    return Other

  def __computeTimeSpend(self, user):
    last_month = timezone.now() - timedelta(days=30)
    log = LogClient.objects.filter(user=user, date__gte=last_month).order_by("-date")
    timeSpend = False
    lastDate = False
    if log:
      for dateConnect in [line.date for line in log]:
        if lastDate:
          diff = lastDate-dateConnect
          if diff < timedelta(seconds=120):
            timeSpend = timeSpend+diff if timeSpend else diff
        lastDate = dateConnect
    return str(timeSpend).split('.', 2)[0] if timeSpend else "_"

  def removeAccount(self, id):
    profile = UserProfile.objects.get(id=int(id))
    user = profile.user
    if profile == self.dataDashboard.userProfile:
      return {"error":"Vous ne pouvez vous supprimer!"}
    LogClient.objects.filter(user=user).delete()
    profile.delete()
    user.delete()
    return {"accountRemoved":id}

  def modifyAccount(self, id, name):
    profile = UserProfile.objects.get(id=int(id))
    user = profile.user
    user.username = name
    user.save()
    return {"accountModified":"OK"}

  def modifyAgent(self, id, name):
    profile = UserProfile.objects.get(id=int(id))
    user = profile.user
    group = user.groups.values_list('name', flat=True)[0]
    if group != "agent":
      return {"error":"Il n'est pas possible de renommer un autre niveau géographique que celui d'un agent."}
    idAgent = profile.idGeo
    agent = AgentSave.objects.get(id=idAgent)
    agent.name = name
    agent.save()
    return {"agentModified":"OK"}

  def setupCreateAccount (self):
    response = {"profile":{"agent":"Secteur", "agentFinitions":"Agent Finition", "drv":"Drv", "root":"Direction Nationale"}}
    dictObject = {"agent":Agent, "agentFinitions":AgentFinitions, "drv":Drv, "root":None}
    for key, classObj in dictObject.items():
      if classObj:
        response[key] = {obj.id:obj.name for obj in classObj.objects.filter(currentYear=True)}
    return response

  def activateCreationAccount(self, dictCreateJson):
    dictData = json.loads(dictCreateJson)
    if not dictData["pseudo"]:
      return {"error":"Le champ pseudo doit obligatoirement être rempli."}
    if User.objects.filter(username=dictData["pseudo"]):
      return {"error":"Ce pseudo est déjà utilisé."}
    if dictData["pwd"] != dictData["confPwd"]:
      return {"error":"Les deux mots de passe diffèrent."}
    userGroup = Group.objects.get(name=dictData["profile"])
    user = User.objects.create_user(username=dictData["pseudo"], password=dictData["pwd"])
    idGeo = dictData["idGeo"] if "idGeo" in dictData else 0
    UserProfile.objects.create(user=user, idGeo=idGeo)
    user.groups.add(userGroup)
    return {"activateCreationAccount":"L'utilisateur a bien été créé"}

# Synonyms

  def paramSynonymsInit(self):
    pdvList = Pdv.objects.filter(sale=True, redistributed=True, currentYear=False)
    for pdv in pdvList and Pdv.object.filter(code=pdv.code, currentYear=True):
      print(f"{pdv.name}; {pdv.code}; {'Oui' if pdv.redistributed else 'Non'}; {'Oui' if pdv.sale else 'Non'}")
    return Synonyms.getDictValues()

  def fillupSynonym(self, dictSynonymJson):
    inversePretty = {value:key for key, value in Synonyms.prettyPrint.items()}
    dictSynonym = json.loads(dictSynonymJson)
    for field, dictValue in dictSynonym.items():
      field = inversePretty[field]
      for originalName, value in dictValue.items():
        Synonyms.setValue(field, originalName, value)
    return {"fillupSynonym":"Les valeurs ont bien été enregistrées"}

# Ad Status Open or Closed
  def switchAdStatus(self):
    isAdOpen = ParamVisio.getValue("isAdOpenSave")
    ParamVisio.setValue("isAdOpenSave", False if isAdOpen else True)
    if not ParamVisio.getValue("isAdOpenSave"):
      for sale in SalesSave.objects.filter(date__isnull=False):
        sale.date = None
        sale.save()
    return {"isAdOpenSave":ParamVisio.getValue("isAdOpenSave"), "isAdOpen":ParamVisio.getValue("isAdOpen")}

# Validation of targets
  def buildValidate(self, target=False):
    titles = {"Drv":10, "Agent":15, "Pdv Code":7, "Date":8, "Pdv":28, "Ancienne valeur":12, "Nouvelle valeur":12}
    if target:
      titles = {"Drv":10, "Agent":15, "Pdv Code":7, "Date":8, "Pdv":28, "Valeur modifiée":15, "Ancienne valeur":12, "Nouvelle valeur":12}
    rawData = {target.pdv:self.__buildValidateLine(target) for target in Target.objects.all() if self.__testValidateLine(target.pdv)}
    dictValue = {"Point de vente redistribué":{}, "Ne vend pas de plaque":{}, "Bassin":{}}
    for pdv, value in rawData.items():
      newValue = json.loads(json.dumps(value[:5]))
      if value[9]:
        newValue.append("Oui" if value[6] else "Non")
        newValue.append("Non" if value[6] else "Oui")
        dictValue["Point de vente redistribué"][pdv.id] = newValue
        newValue = json.loads(json.dumps(value[:5]))
      if value[10]:
        newValue.append("Oui" if value[7] else "Non")
        newValue.append("Non" if value[7] else "Oui")
        dictValue["Point de vente redistribué finition"][pdv.id] = newValue
        newValue = json.loads(json.dumps(value[:5]))
      if value[8]:
        newValue.append("Oui" if value[5] else "Non")
        newValue.append("Non" if value[5] else "Oui")
        dictValue["Ne vend pas de plaque"][pdv.id] = newValue
        newValue = json.loads(json.dumps(value[:5]))
      if value[11] and value[11] != pdv.bassin.name:
        newValue += [pdv.bassin.name.replace("Négoce_", ""), value[11]]
        dictValue["Bassin"][pdv.id] = newValue
    return {"titles":titles, "values":dictValue}

  def __buildValidateLine(self, target):
    pdvId = target.pdv.id
    pdv = PdvSave.objects.get(id=pdvId)
    return [pdv.drv.name, pdv.agent.name, pdv.code, target.date.strftime('%Y-%m-%d'), pdv.name, target.sale, target.redistributed, target.redistributedFinitions, target.sale != pdv.sale, target.redistributed != pdv.redistributed, target.redistributedFinitions != pdv.redistributedFinitions, target.bassin]

  def __testValidateLine(self, pdv):
    return pdv.available and pdv.sale and pdv.redistributed and pdv.currentYear


  def updateValidate(self, dictValidate):
    listData = json.loads(dictValidate)
    for dictPdv in listData["modify"]:
      pdv = PdvSave.objects.get(id=dictPdv["pdvId"])
      if dictPdv["action"] == "Point de vente redistribué":
        pdv.redistributed = dictPdv["value"]
      elif dictPdv["action"] == "Point de vente redistribué finition":
        pdv.redistributedFinitions = dictPdv["value"]
      elif dictPdv["action"] == "Ne vend pas de plaque":
        pdv.sale = dictPdv["value"]
      pdv.save()
    for dictPdv in listData["delete"]:
      pdv = Pdv.objects.get(id=dictPdv["pdvId"])
      target = Target.objects.get(pdv=pdv)
      if dictPdv["action"] == "Point de vente redistribué":
        target.redistributed = dictPdv["value"]
      elif dictPdv["action"] == "Point de vente redistribué finition":
        target.redistributedFinitions = dictPdv["value"]
      elif dictPdv["action"] == "Ne vend pas de plaque":
        target.sale = dictPdv["value"]
      target.save()
    return self.buildValidate()
    
  

