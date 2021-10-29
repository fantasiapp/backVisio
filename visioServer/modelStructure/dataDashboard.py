from ..models import *
import json
import os
from django.utils import timezone
from dotenv import load_dotenv

load_dotenv()

class DataDashboard:
  currentYear = "currentYear"
  __flagLoad = True
  
  def __init__(self, userProfile, userGeoId, userGroup, isNotOnServer):
    """engendre les données complètes (niveau national) et sauve les données dans des attributs de classe"""
    self.__userGeoId = userGeoId
    self.__userGroup = userGroup
    self.__userProfile = userProfile
    if DataDashboard.__flagLoad:
      DataDashboard.__flagLoad = False
      print("loading data in RAM")
      for name, model in CommonModel.computeTableClass():
        DataDashboard.createFromModel(model, name, isNotOnServer)
      DataDashboard.__geoTreeStructure = json.loads(os.getenv('GEO_TREE_STRUCTURE'))
      DataDashboard.__tradeTreeStructure = json.loads(os.getenv('TRADE_TREE_STRUCTURE'))
      self._computeTargetLevel()
      params = getattr(self, "__params")
    params["pseudo"] = userProfile.user.username
    if getattr(self, "__pdvs", False) and getattr(self, "__pdvs_ly", False):
      self.dictLocalPdv = self.__computeListPdv()
    else:
      # happen when initialisation is not finished and someone send a query
      print("initialisation is not Finished")

  @classmethod
  def createFromModel(cls, model, name, isNotOnServer):
    if name == "pdvs" and isNotOnServer:
      return cls.__createFromJson()
    if len(model.listFields()) > 1:
      setattr(cls, f"__structure{name.capitalize()}", model.listFields())
    indexes = model.listIndexes()
    if len(indexes) != 0:
      setattr(cls, f"__indexes{name.capitalize()}", indexes)
    setattr(cls, f"__{name}", model.dictValues())
    if hasattr(model, "currentYear"):
      setattr(cls, f"__{name}_ly", model.dictValues(currentYear=False))

  @classmethod
  def __createFromJson(cls):
    """Fonction ayant pour but d'aller chercher les pdv dans des json pour la mise au point: le chargement est alors instantané"""
    setattr(cls, "__indexesPdvs", Pdv.listIndexes())
    setattr(cls, "__structurePdvs", Pdv.listFields())
    if not os.path.isfile("./visioServer/modelStructure/pdvDict.json"):
      with open("./visioServer/modelStructure/pdvDict.json", 'w') as jsonFile:
        json.dump(Pdv.dictValues(), jsonFile, indent = 3)
      with open("./visioServer/modelStructure/pdvDict_ly.json", 'w') as jsonFile:
        json.dump(Pdv.dictValues(currentYear=False), jsonFile, indent = 3)
    with open("./visioServer/modelStructure/pdvDict.json") as jsonFile:
      pdvs = {int(id):value for id, value in json.load(jsonFile).items()}
    setattr(cls, "__pdvs", pdvs)
    with open("./visioServer/modelStructure/pdvDict_ly.json") as jsonFile:
      pdvs = {int(id):value for id, value in json.load(jsonFile).items()}
    setattr(cls, "__pdvs_ly", pdvs)

  def insertModel(self, data, name, model):
    listAttr = [f"__structure{name.capitalize()}", f"__indexes{name.capitalize()}", f"__{name}"]
    for attr in listAttr:
      DataDashboard.currentYear = "currentYear"
      if hasattr(self, attr):
        listId = model.computeListId(self, data)
        if attr == f"__{name}" and (isinstance(listId, list) or isinstance(listId, set)):
          data[attr[2:]] = {id:value for id, value in getattr(self, attr).items() if id in listId}
        else:
          data[attr[2:]] = getattr(self, attr)
      attr += "_ly"
      if hasattr(self, attr):
        DataDashboard.currentYear = "lastYear"
        listId = model.computeListId(self, data)
        if attr == f"__{name}_ly" and (isinstance(listId, list) or isinstance(listId, set)):
          data[attr[2:]] = {id:value for id, value in getattr(self, attr).items() if id in listId}
        else:
          data[attr[2:]] = getattr(self, attr)

  @property
  def userGroup(self): return self.__userGroup

  @property
  def userGeoId(self): return self.__userGeoId
  
  @property
  def dataQuery(self):
    firstLevel = self.__userGeoId if self.__userGroup != "root" else 0
    data = {
      "structureLevel":TreeNavigation.listFields(),
      "levelGeo":self._computeLocalLevel("geo", True),
      "levelTrade":self._computeLocalLevel("trade", True),
      "levelGeo_ly":self._computeLocalLevel("geo", False),
      "levelTrade_ly":self._computeLocalLevel("trade", False),
      "geoTree":self._computeLocalGeoTree("currentYear"),
      "tradeTree":self._buildTree(firstLevel, DataDashboard.__tradeTreeStructure, self.dictLocalPdv["currentYear"]),
      "geoTree_ly":self._computeLocalGeoTree("lastYear"),
      "tradeTree_ly":self._buildTree(firstLevel, DataDashboard.__tradeTreeStructure, self.dictLocalPdv["lastYear"]),
      "structureTarget":Target.listFields(),
      "structureSales":Sales.listFields(),
      }
    for name, model in CommonModel.computeTableClass():
      self.insertModel(data, name, model)
    TargetLevel.dictValuesFiltered(self, data)
    self._setupFinitions(data)
    return data

  def __computeListPdv(self):
    result = {}
    for currentYear in ["currentYear", "lastYear"]:
      dictPdvs = "__pdvs" if currentYear=="currentYear" else "__pdvs_ly"
      if self.__userGroup != "root":
        indexPdv = Pdv.listFields().index(self.__userGroup)
        result[currentYear] = {id:values for id, values in getattr(self, dictPdvs).items() if values[indexPdv] == self.__userGeoId}
      else:
        result[currentYear] = getattr(self, dictPdvs)
    return result

  def _computeLocalLevel(self, geoOrTrade, currentYear):
    profile = Group.objects.get(name=self.userGroup)
    localLevel = TreeNavigation.objects.get(profile=profile, levelName=profile.name, geoOrTrade=geoOrTrade, currentYear=currentYear).listValues
    return localLevel

  def _computeLocalGeoTree(self, currentYear):
    if self.userGroup == "root":
      attr = "__pdvs" if currentYear == "currentYear" else "__pdvs_ly"
      return self._buildTree(0, DataDashboard.__geoTreeStructure, getattr(DataDashboard, attr))
    indexStart = 1 if self.userGroup == "drv" else 2
    return self._buildTree(self.__userGeoId, DataDashboard.__geoTreeStructure[indexStart:], self.dictLocalPdv[currentYear])

  def _setupFinitions(self, data):
    self.__userProfile.lastUpdate = timezone.now() - timezone.timedelta(seconds=5)
    self.__userProfile.save()
    data["timestamp"] = self.__userProfile.lastUpdate.timestamp()
    if self.__userGroup == "root":
      data["root"] = {0:""}
    # if self.__userGroup in ["agent", "agentFinitions"]:
    #   del data["drv"]
    #   del data["drv_ly"]

  @classmethod
  def _buildTree(cls, idLevel, steps:list, pdvs:dict):
    """idLevel = idLevel of first node, root for instance
    step = the list of stepId following the root node
    pdvs is a dictionary with keys : the ids and the list of values with dataSales"""
    if not steps:
        return [idLevel, list(pdvs.keys())]
    nextKey = steps[0]
    children = [cls._buildTree(idLevel, steps[1:], associatedPdvs) for idLevel, associatedPdvs in cls._diceByKey(nextKey, pdvs).items()]
    return [idLevel, children]
  
  @classmethod
  def _diceByKey(cls, index:int, pdvs:dict):
    dicedBykey = {}
    for id, pdv in pdvs.items():
      if pdv[index] not in dicedBykey:
        dicedBykey[pdv[index]] = {}
      dicedBykey[pdv[index]][id] = pdv
    return dicedBykey

  @classmethod
  def _computeTargetLevel(cls):
    for currentYear in [True, False]:
      ext = "" if currentYear else "_ly"
      dictTargets = TargetLevel.dictValues(currentYear)
      for key, values in dictTargets.items():
        setattr(cls, f"__targetLevel{key.capitalize()}{ext}", values)

  #queries for updates
  def getUpdate(self, nature):
    listIdPdv = list(self.dictLocalPdv["currentYear"].keys()) if self.__userGroup != "root" else False
    lastUpdate = self.__userProfile.lastUpdate
    now = timezone.now()
    if nature == "request":
      return self.__getUpdateRequest(lastUpdate, listIdPdv)
    elif nature == "acknowledge":
        self.__userProfile.lastUpdate = now - timezone.timedelta(seconds=5)
        self.__userProfile.save()
        return {"message":"getUpdate acknowledge received", "timestamp":self.__userProfile.lastUpdate.timestamp()}
    else:
      return {"error":f"wrong nature received : {nature}"}

  def __getUpdateRequest(self,lastUpdate, listIdPdv):
    listData = LogUpdate.objects.filter(date__gte=lastUpdate) if lastUpdate else LogUpdate.objects.all()
    if not listData: return {"message":"nothing to Update"}
    listUpdate = [json.loads(logUpdate.data) for logUpdate in listData]
    jsonToSend = {key:{} for key in listUpdate[0].keys()}
    for dictUpdate in listUpdate:
      for nature, dictNature in dictUpdate.items():
        for id, listObject in dictNature.items():
          if nature == "pdvs":
            if not listIdPdv or int(id) in listIdPdv:
              jsonToSend["pdvs"][id] = listObject
          else:
            jsonToSend[nature][id] = listObject
    print("update request", jsonToSend)
    return jsonToSend

  def postUpdate(self, userName, jsonString):
    print("post update", userName, jsonString)
    user = User.objects.get(username=userName)
    try:
      jsonData = json.loads(jsonString)
      now = self.__updateDatabasePdv(jsonData)
      self.__updateDatabaseTargetLevel(jsonData, now)
      if "logs" in jsonData:
        self.__updateLogClient(jsonData["logs"], now)
        del jsonData["logs"]
      flagSave = False
      for value in jsonData.values():
        if value: flagSave = True
      if flagSave:
        LogUpdate.objects.create(date=now, user=user, data=json.dumps(jsonData))
      return {"message":"postUpdate received"}
    except:
      return {"error":"postUpdate body is not json"}

  def __updateDatabasePdv(self, data):
    now = timezone.now()
    if "pdvs" in data:
      for id, value in data["pdvs"].items():
        pdv = Pdv.objects.get(id=int(id))
        getattr(self, "__pdvs")[int(id)] = pdv.update(value, now)
    return now

  def __updateDatabaseTargetLevel(self, data, now):
    for key, dictTargetLevel in data.items():
      if key != "pdvs" and key != "logs" and dictTargetLevel:
        if key == "targetLevelDrv":
          for idDrv, listTargetLevel in dictTargetLevel.items():
            drv = Drv.objects.get(id=idDrv)
            targetLevel = TargetLevel.objects.get(drv=drv, currentYear=True)
            newValues = targetLevel.update(listTargetLevel, now)
            if newValues:
              getattr(self, "__targetLevelDrv")[int(idDrv)] = newValues
        if key == "targetLevelAgentP2CD":
          for idAgent, listTargetLevel in dictTargetLevel.items():
            agent = Agent.objects.get(id=idAgent)
            targetLevel = TargetLevel.objects.get(agent=agent, currentYear=True)
            newValues =  targetLevel.update(listTargetLevel, now)
            if newValues:
              getattr(self, "__targetLevelAgent")[int(idAgent)] = newValues
        if key == "targetLevelAgentFinitions":
          for idAF, listTargetLevel in dictTargetLevel.items():
            af = AgentFinitions.objects.get(id=idAF)
            targetLevel = TargetLevel.objects.get(agentFinitions=af, currentYear=True)
            newValues = targetLevel.update(listTargetLevel, now)
            if newValues:
              getattr(self, "__targetLevelAgentfinitions")[int(idAF)] = newValues

  def __updateLogClient(self, listLogs, now):
    for log in listLogs:
      LogClient.createFromList(log, self.__userProfile, now)