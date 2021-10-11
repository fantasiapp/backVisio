from sys import flags
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
  __structureLevel = ['levelName', 'prettyPrint', 'listDashBoards', 'subLevel']
  __levelGeo = None
  __structureTargetLevelDrv = ["volP2CD", "dnP2CD", "volFinition", "dnFinition"]
  __structureTargetLevelAgentP2CD = ["volP2CD", "dnP2CD"]
  __structureTargetLevelAgentFinition = ["volFinition", "dnFinition"]
  

  def __init__(self, userGeoId, userGroup, isNotOnServer):
    """engendre les données complètes (niveau national) et sauve les données dans des attributs de classe"""
    self.__userGeoId = userGeoId
    self.__userGroup = userGroup
    if not DataDashboard.__levelGeo:
      for name, model in CommonModel.computeTableClass():
        DataDashboard.createFromModel(model, name, isNotOnServer)
      DataDashboard.__levelGeo = DataDashboard._computeLevels(TreeNavigation, "geo")
      DataDashboard.__levelTrade = DataDashboard._computeLevels(TreeNavigation, "trade")
      DataDashboard.__geoTreeStructure = json.loads(os.getenv('GEO_TREE_STRUCTURE'))
      DataDashboard.__geoTree = self._buildTree(0, DataDashboard.__geoTreeStructure, getattr(DataDashboard, "__pdvs"))
      DataDashboard.__tradeTreeStructure = json.loads(os.getenv('TRADE_TREE_STRUCTURE'))
      DataDashboard.__tradeTree = self._buildTree(0, DataDashboard.__tradeTreeStructure, getattr(DataDashboard, "__pdvs"))
      self._computeTargetLevel()

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

  @classmethod
  def __createFromJson(cls):
    setattr(cls, "__indexesPdvs", Pdv.listIndexes())
    setattr(cls, "__structurePdvs", Pdv.listFields())
    if not os.path.isfile("./visioServer/modelStructure/pdvDict.json"):
      with open("./visioServer/modelStructure/pdvDict.json", 'w') as jsonFile:
        json.dump(Pdv.dictValues(), jsonFile, indent = 3)
    with open("./visioServer/modelStructure/pdvDict.json") as jsonFile:
      pdvs = {int(id):value for id, value in json.load(jsonFile).items()}
    setattr(cls, "__pdvs", pdvs)

  def insertModel(self, data, name, model):
    listAttr = [f"__structure{name.capitalize()}", f"__indexes{name.capitalize()}", f"__{name}"]
    for attr in listAttr:
      if hasattr(self, attr):
        listId = model.computeListId(self, data)
        if attr == f"__{name}" and (isinstance(listId, list) or isinstance(listId, set)):
          data[attr[2:]] = {id:value for id, value in getattr(self, attr).items() if id in listId}
        else:
          data[attr[2:]] = getattr(self, attr)

  @property
  def userGroup(self): return self.__userGroup
  
  @property
  def dataQuery(self):
    data = {
      "structureLevel":DataDashboard.__structureLevel,
      "levelGeo":self._computeLocalLevels(DataDashboard.__levelGeo, self.__userGroup),
      "levelTrade": DataDashboard.__levelTrade,
      "geoTree":self._computeLocalGeoTree(),
      "tradeTree":DataDashboard.__tradeTree,
      "structureTarget":Ciblage.listFields(),
      "structureSales":Ventes.listFields(),
      }
    for name, model in CommonModel.computeTableClass():
      self.insertModel(data, name, model)
    self. _computeLocalTargetLevel(data)
    return data

  def _computeLocalLevels(self, originLevel:list, selectedLevel:str):
    if originLevel[0] == selectedLevel:
      return originLevel
    return self._computeLocalLevels(originLevel[3], selectedLevel)

  def _computeLocalGeoTree(self):
    if self.__userGroup == "root":
      return DataDashboard.__geoTree
    if self.__userGroup == "drv":
      for drv in DataDashboard.__geoTree[1]:
        if drv[0] == self.__userGeoId:
          return drv
    hierarchy = self.__computeHierarchy()
    drvId = [couple[0] for couple in hierarchy if couple[1] == self.__userGeoId][0]
    for drv in DataDashboard.__geoTree[1]:
        if drv[0] == drvId:
          for agent in drv[1]:
            if agent[0] == self.__userGeoId:
              return agent

  def __computeHierarchy(self) -> list:
    """Hierachy is a list of couples containing drvId dans agentId"""
    hierarchy = []
    for drv in DataDashboard.__geoTree[1]:
      drvId = drv[0]
      for agent in drv[1]:
        hierarchy.append((drvId, agent[0]))
    return hierarchy

  def _computeLocalTargetLevel(self, data):
    if self.__userGroup == "root":
      data["structureTargetLevelDrv"] = self.__structureTargetLevelDrv
      data["targetLevelDrv"] = self.__targetLevelDrv
      data["structureTargetLevelAgentP2CD"] = self.__structureTargetLevelAgentP2CD
      data["targetLevelAgentP2CD"] = self.__targetLevelAgentP2CD
      data["structureTargetLevelAgentFinition"] = self.__structureTargetLevelAgentFinition
      data["targetLevelAgentFinition"] = self.__targetLevelAgentFinition
    elif self.__userGroup == "drv":
      indexDrv, indexAgent = data["structurePdvs"].index("drv"), data["structurePdvs"].index("agent")
      listAgentId = [line[indexAgent] for line in data["pdvs"].values() if line[indexDrv] == self.__userGeoId]
      data["structureTargetLevelDrv"] = self.__structureTargetLevelDrv
      data["targetLevelDrv"] = {id:level for id, level in self.__targetLevelDrv.items() if id == self.__userGeoId}
      data["structureTargetLevelAgentP2CD"] = self.__structureTargetLevelAgentP2CD
      data["targetLevelAgentP2CD"] = {id:value for id, value in self.__targetLevelAgentP2CD.items() if id in listAgentId}
      data["structureTargetLevelAgentFinition"] = self.__structureTargetLevelAgentFinition
      data["targetLevelAgentFinition"] = {id:level for id, level in self.__targetLevelAgentFinition.items() if level[0] == self.__userGeoId}
    elif self.__userGroup == "agent":
      data["structureTargetLevelAgentP2CD"] = self.__structureTargetLevelAgentP2CD
      data["targetLevelAgentP2CD"] = {id:value for id, value in self.__targetLevelAgentP2CD.items() if id == self.__userGeoId}
  
  @classmethod
  def _computeLevels(cls, classObject, geoOrTrade):
    listLevel = {object.id:object for object in classObject.objects.filter(geoOrTrade=geoOrTrade)}
    dictLevelWithDashBoard = {}
    for object in listLevel.values():
      dictLevelWithDashBoard[object.id] = list(model_to_dict(object).values())
      del dictLevelWithDashBoard[object.id][0]
      del dictLevelWithDashBoard[object.id][0]
      dashBoardTree = DashboardTree.objects.filter(geoOrTrade=geoOrTrade, level=object).first()
      dictLevelWithDashBoard[object.id].insert(2, [dashboard.id for dashboard in dashBoardTree.dashboards.all()])
    for level in dictLevelWithDashBoard.values():
      if level[3]:
        dictLevelWithDashBoard[level[3]][3] = level
    level.pop()
    return list(dictLevelWithDashBoard.values())[0]

  @classmethod
  def _buildTree(cls, name, steps:list, pdvs:dict):
    """name = name of first node, root for instance
    step = the list of stepId following the root node
    pdvs is a dictionary with keys : the ids and the list of values with dataSales"""
    if not steps:
        return [name, list(pdvs.keys())]
    nextKey = steps[0]
    children = [cls._buildTree(name, steps[1:], associatedPdvs) for name, associatedPdvs in cls._diceByKey(nextKey, pdvs).items()]
    return [name, children]
  
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
    cls.__targetLevelDrv, cls.__targetLevelAgentP2CD, cls.__targetLevelAgentFinition = {}, {}, {}
    for tlObject in CiblageLevel.objects.all():
      if tlObject.drv:
        cls.__targetLevelDrv[tlObject.drv.id] = [tlObject.volP2CD, tlObject.dnP2CD, tlObject.volFinition, tlObject.dnFinition]
      else:
        if tlObject.volP2CD or tlObject.dnP2CD:
          cls.__targetLevelAgentP2CD[tlObject.agent.id] = [tlObject.volP2CD, tlObject.dnP2CD]
        if tlObject.volFinition or tlObject.volFinition:
          cls.__targetLevelAgentFinition[tlObject.agent.id] = [tlObject.volFinition, tlObject.dnFinition]

  #queries for updates

  def getUpdate(self, userProfile, nature):
    geoTree = False if self.__userGroup == "root" else self._computeLocalGeoTree()
    data = {"geoTree":geoTree}
    lastUpdate = userProfile.lastUpdate
    listIdPdv = False if self.__userGroup == "root" else Pdv.computeListId(self, data)
    now = timezone.now()
    if nature == "request":
      listData = LogUpdate.objects.filter(date__gte=lastUpdate) if lastUpdate else LogUpdate.objects.all()
      if not listData: return {"message":"nothing to Update"}
      listUpdate = [json.loads(logUpdate.data) for logUpdate in listData]
      if listUpdate:
        jsonToSend = {key:{} for key in listUpdate[0].keys()}
        for dictUpdate in listUpdate:
          for nature, dictNature in dictUpdate.items():
            for id, listObject in dictNature.items():
              if nature == "pdvs":
                if not listIdPdv or id in listIdPdv:
                  jsonToSend["pdvs"][id] = listObject
              else:
                jsonToSend[nature][id] = listObject
        return jsonToSend  
    elif nature == "acknowledge":
        userProfile.lastUpdate = now - timezone.timedelta(seconds=5)
        userProfile.save()
        return {"message":"getUpdate acknowledge received"}
    else:    
      return {"error":f"wrong nature received : {nature}"}

  def postUpdate(self, userName, jsonString):
    user = User.objects.get(username=userName)
    try:
      jsonData = json.loads(jsonString)
      now = self.__updateDatabasePdv(jsonData)
      self.__updateDatabaseTargetLevel(jsonData, now)
      LogUpdate.objects.create(date=now, user=user, data=jsonString)
      return {"message":"postUpdate received"}
    except:
      return {"error":"postUpdate body is not json"}

  def __updateDatabasePdv(self, data):
    now = timezone.now()
    if "pdvs" in data:
      indexSales = getattr(self, "__structurePdvs").index("sales")
      for id, value in data["pdvs"].items():
        pdv = Pdv.objects.get(id=id)
        pdvInRam = getattr(DataDashboard, "__pdvs")[int(id)]
        self.__updateDataBaseTarget(value, pdv, now, pdvInRam)
        salesInRam = pdvInRam[indexSales]
        sales = value[indexSales]
        for saleImported in sales:
          if saleImported[3]:
            salesObject = Ventes.objects.filter(pdv=id, industry=saleImported[1], product=saleImported[2])
            if salesObject:
              saleObject = salesObject[0]
              if abs(saleObject.volume - saleImported[3]) >= 1:
                if self.__updateSaleRam(salesInRam, saleImported, now):
                  saleObject.volume = saleImported[3]
                  saleObject.date = now
                  saleObject.save()
            else:
              industry = Industrie.objects.get(id=saleImported[1])
              product = Produit.objects.get(id=saleImported[2])
              Ventes.objects.create(date=now, pdv=pdv, industry=industry, product=product, volume=float(saleImported[3]), currentYear=True)
              salesInRam.append([now.timestamp()] + saleImported[1:])
    return now


  def __updateDataBaseTarget(self, valueReceived, pdv, now, pdvInRam):
    indexTarget = getattr(self, "__structurePdvs").index("target")
    target = valueReceived[indexTarget]
    targetObject = Ciblage.objects.filter(pdv=pdv)
    flagSave = False
    if targetObject:
      print("update target save", target)
      flagSave = targetObject[0].update(target, now)
    else:
      print("need to Create Target Object", target, valueReceived)
      flagSave = Ciblage.createFromList(target, pdv, now)
    if flagSave:
      pdvInRam[indexTarget] = target
      print("__updateDataBaseTarget saved in Ram", pdvInRam)

  def __updateSaleRam(self, salesInRam, saleImported, now):
    for saleInRam in salesInRam:
      if saleInRam[1]  == saleImported[1] and saleInRam[2]  == saleImported[2]:
        saleInRam[0] = now.timestamp()
        saleInRam[3] = saleImported[3]
        return True
      return False

  def __updateDatabaseTargetLevel(self, data, now):
    for key, dictTargetLevel in data.items():
      if key != "pdvs" and dictTargetLevel:
        if key == "targetLevelDrv":
          for idDrv, listTargetLevel in dictTargetLevel.items():
            drv = Drv.objects.get(id=idDrv)
            targetLevel = CiblageLevel.objects.get(drv=drv)
            targetLevel.date = now
            targetLevel.volP2CD = float(listTargetLevel[0]) if listTargetLevel[0] else 0.0
            targetLevel.dnP2CD = int(listTargetLevel[1]) if listTargetLevel[1] else 0
            targetLevel.volFinition = float(listTargetLevel[2]) if listTargetLevel[2] else 0.0
            targetLevel.save()
            DataDashboard.__targetLevelDrv[idDrv] = listTargetLevel
        if key == "targetLevelAgentP2CD":
          for idAgent, listTargetLevel in dictTargetLevel.items():
            agent = Agent.objects.get(id=idAgent)
            targetLevel = CiblageLevel.objects.get(agent=agent)
            targetLevel.date = now
            targetLevel.volP2CD = float(listTargetLevel[0]) if listTargetLevel[0] else 0.0
            targetLevel.dnP2CD = int(listTargetLevel[1]) if listTargetLevel[1] else 0
            targetLevel.save()
            DataDashboard.__targetLevelAgentP2CD[idAgent] = listTargetLevel