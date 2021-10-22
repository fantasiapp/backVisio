from ..models import *
import json
from django.conf import settings
from django.forms.models import model_to_dict
from django.db.models.fields.related import ForeignKey
from ..utils import camel
import os
from django.utils import timezone
from dotenv import load_dotenv

load_dotenv()

class DataDashboard:
  __levelGeo = None
  __structureTargetLevel = ["vol", "dn"]
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
    self.dictLocalPdv = self.__computeListPdv()

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
  def dataQuery(self):
    firstLevel = self.__userGeoId if self.__userGroup != "root" else 0
    data = {
      "structureLevel":TreeNavigation.listFields(),
      "levelGeo":self._computeLocalLevel("geo"),
      "levelTrade":self._computeLocalLevel("trade"),
      "geoTree":self._computeLocalGeoTree("currentYear"),
      "geoTree_ly":self._computeLocalGeoTree("lastYear"),
      "tradeTree":self._buildTree(firstLevel, DataDashboard.__tradeTreeStructure, self.dictLocalPdv["currentYear"]),
      "tradeTree_ly":self._buildTree(self.__lastYearId, DataDashboard.__tradeTreeStructure, self.dictLocalPdv["lastYear"]),
      "structureTarget":Target.listFields(),
      "structureSales":Sales.listFields(),
      }
    for name, model in CommonModel.computeTableClass():
      self.insertModel(data, name, model)
    self._computeLocalTargetLevel(data)
    self._setupFinitions(data)
    return data

  @property
  def __lastYearId(self):
    if self.__userGroup == "root": return 0
    model = Drv
    if self.__userGroup == "agent":
      model = Agent
    elif self.__userGroup == "agentFinitions":
      model = AgentFinitions
    nameRegion = model.objects.get(id=self.__userGeoId)
    return model.objects.get(name=nameRegion, currentYear=False).id

  def __computeListPdv(self):
    result = {}
    for currentYear in ["currentYear", "lastYear"]:
      dictPdvs = "__pdvs" if currentYear=="currentYear" else "__pdvs_ly"
      if self.__userGroup != "root":
        indexActor = self.__userGeoId if currentYear == "currentYear" else self.__lastYearId
        indexPdv = Pdv.listFields().index(self.__userGroup)
        result[currentYear] = {id:values for id, values in getattr(self, dictPdvs).items() if values[indexPdv] == indexActor}
      else:
        result[currentYear] = getattr(self, dictPdvs)
    return result

  def _computeLocalLevel(self, geoOrTrade):
    levelName = "agent" if self.userGroup == "agentFinitions" else self.userGroup
    levelName = "root" if geoOrTrade == "trade" else levelName
    localLevel = TreeNavigation.objects.get(levelName=levelName, geoOrTrade=geoOrTrade).listValues
    if self.userGroup in ["agent", "agentFinitions"]:
      TreeNavigation.removeDashboards(localLevel, self.userGroup, geoOrTrade)
    return localLevel

  def _computeLocalGeoTree(self, currentYear):
    if self.userGroup == "root":
      attr = "__pdvs" if currentYear == "currentYear" else "__pdvs_ly"
      return self._buildTree(0, DataDashboard.__geoTreeStructure, getattr(DataDashboard, attr))
    indexAgent = self.__userGeoId if currentYear == "currentYear" else self.__lastYearId
    indexStart = 1 if self.userGroup == "drv" else 2
    return self._buildTree(indexAgent, DataDashboard.__geoTreeStructure[indexStart:], self.dictLocalPdv[currentYear])

  def _computeLocalTargetLevel(self, data):
    data["structureTargetlevel"] = self.__structureTargetLevel
    if self.__userGroup == "root":
      data["targetLevelDrv"] = self.__targetLevelDrv
      data["targetLevelAgentP2CD"] = self.__targetLevelAgentP2CD
      data["targetLevelAgentFinitions"] = self.__targetLevelAgentFinitions
      data["targetLevelDrv_ly"] = self.__targetLevelDrv_ly
      data["targetLevelAgentP2CD_ly"] = self.__targetLevelAgentP2CD_ly
      data["targetLevelAgentFinitions_ly"] = self.__targetLevelAgentFinitions_ly
    elif self.__userGroup == "drv":
      indexDrv, indexAgent = data["structurePdvs"].index("drv"), data["structurePdvs"].index("agent")
      for ext in ["", "_ly"]:
        selectedDrv = self.__lastYearId if ext else self.__userGeoId
        listAgentId = set([line[indexAgent] for line in data["pdvs" + ext].values() if line[indexDrv] == selectedDrv])
        if ext:
          field = {"drv":self.__targetLevelDrv_ly, "agent":self.__targetLevelAgentP2CD_ly, "fin":self.__targetLevelAgentFinitions_ly}
        else:
          field = {"drv":self.__targetLevelDrv, "agent":self.__targetLevelAgentP2CD, "fin":self.__targetLevelAgentFinitions}
        data["targetLevelDrv" + ext] = {id:level for id, level in field["drv"].items() if id == selectedDrv}
        data["targetLevelAgentP2CD"+ext] = {id:level for id, level in field["agent"].items() if id in listAgentId}
        data["targetLevelAgentFinitions"+ext] = {id:level for id, level in field["fin"].items() if self.__isFinDrv(id, selectedDrv, ext)}
    else:
      targetLevel = "targetLevelAgentP2CD" if self.__userGroup == "agent" else "targetLevelAgentFinitions"
      data[targetLevel] = {id:value for id, value in self.__targetLevelAgentP2CD.items() if id == self.__userGeoId}
      data[targetLevel+"_ly"] = {id:value for id, value in self.__targetLevelAgentP2CD_ly.items() if id == self.__lastYearId}

  def __isFinDrv(self, idFin, idDrv, currentYear):
    lineFin = getattr(self, f"__agentFinitions{currentYear}")[idFin]
    return AgentFinitions.getDataFromDict("drv", lineFin) == idDrv

  def _setupFinitions(self, data):
    self.__userProfile.lastUpdate = timezone.now() - timezone.timedelta(seconds=5)
    self.__userProfile.save()
    data["timestamp"] = self.__userProfile.lastUpdate.timestamp()
    if self.__userGroup == "root":
      data["root"] = {0:""}
    else:
      for index in range(2):
        data["levelTrade"][index] = data["levelGeo"][index]

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
    cls.__targetLevelDrv, cls.__targetLevelAgentP2CD, cls.__targetLevelAgentFinitions = {}, {}, {}
    cls.__targetLevelDrv_ly, cls.__targetLevelAgentP2CD_ly, cls.__targetLevelAgentFinitions_ly = {}, {}, {}
    dictTarget = {
      "currentYear":{"drv":cls.__targetLevelDrv, "agent":cls.__targetLevelAgentP2CD, "finition":cls.__targetLevelAgentFinitions},
      "lastYear":{"drv":cls.__targetLevelDrv_ly, "agent":cls.__targetLevelAgentP2CD_ly, "finition":cls.__targetLevelAgentFinitions_ly}
      }
    for year, targets in dictTarget.items():
      for tlObject in TargetLevel.objects.filter(currentYear=year=="currentYear"):
        if tlObject.drv:
          targets["drv"][tlObject.drv.id] = [tlObject.vol, tlObject.dn]
        else:
          if tlObject.vol or tlObject.dn:
            if tlObject.agent:
              targets["agent"][tlObject.agent.id] = [tlObject.vol, tlObject.dn]
            else:
              targets["finition"][tlObject.agentFinitions.id] = [tlObject.vol, tlObject.dn]

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
    return jsonToSend

  def postUpdate(self, userName, jsonString):
    user = User.objects.get(username=userName)
    try:
      jsonData = json.loads(jsonString)
      now = self.__updateDatabasePdv(jsonData)
      print("pdv updated")
      self.__updateDatabaseTargetLevel(jsonData, now)
      print("targetLevel updated")
      self.__updateLogClient(jsonData["logs"], now)
      print("log updated")
      del jsonData["logs"]
      flagSave = False
      for value in jsonData.values():
        if value: flagSave = True
      if flagSave:
        print("saveLogUpdate", json.dumps(jsonData))
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
            print("targetLevelDrv", idDrv, listTargetLevel)
            drv = Drv.objects.get(id=idDrv)
            targetLevel = TargetLevel.objects.get(drv=drv, currentYear=True)
            targetLevel.update(listTargetLevel, now)
            DataDashboard.__targetLevelDrv[int(idDrv)] = listTargetLevel
        if key == "targetLevelAgentP2CD":
          for idAgent, listTargetLevel in dictTargetLevel.items():
            print("targetLevelAgentP2CD", idAgent, listTargetLevel)
            agent = Agent.objects.get(id=idAgent)
            targetLevel = TargetLevel.objects.get(agent=agent, currentYear=True)
            targetLevel.update(listTargetLevel, now)
            DataDashboard.__targetLevelAgentP2CD[int(idAgent)] = listTargetLevel
        if key == "targetLevelAgentFinitions":
          for idAF, listTargetLevel in dictTargetLevel.items():
            print("targetLevelAgentFinitions", idAF, listTargetLevel)
            af = AgentFinitions.objects.get(id=idAF)
            print(af)
            targetLevel = TargetLevel.objects.get(agentFinitions=af, currentYear=True)
            print(targetLevel)
            targetLevel.update(listTargetLevel, now)
            DataDashboard.__targetLevelAgentFinitions[int(idAF)] = listTargetLevel

  def __updateLogClient(self, listLogs, now):
    for log in listLogs:
      print("__updateLogClient", log)
      LogClient.createFromList(log, self.__userProfile, now)