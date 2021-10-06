from ..models import *
import json
from django.conf import settings
from django.forms.models import model_to_dict
from django.db.models.fields.related import ForeignKey
from ..utils import camel
import os
from dotenv import load_dotenv

load_dotenv()

class DataDashboard:
  __structureLevel = ['levelName', 'prettyPrint', 'listDashBoards', 'subLevel']
  __levelGeo = None
  __structureTargetLevelDrv = ["volP2CD", "dnP2CD", "volFinition", "dnFinition"]
  __structureTargetLevelAgentP2CD = ["volP2CD", "dnP2CD"]
  __structureTargetLevelAgentFinition = ["volFinition", "dnFinition"]
  

  def __init__(self, userGeoId, userGroup, isNotOnServer):
    self.__userGeoId = userGeoId
    self.__userGroup = userGroup
    if not DataDashboard.__levelGeo:
      dictModel = {
        "pdvs":Pdv, "dashboards":Dashboard, "layout":Layout, "widget":Widget, "widgetParams":WidgetParams, "widgetCompute":WidgetCompute, "params":ParamVisio,
        "labelForGraph":LabelForGraph, "axisForGraph": AxisForGraph, "segmentMarketing":SegmentMarketing, "segmentCommercial":SegmentCommercial, "enseigne":Enseigne, "ensemble":Ensemble, "sousEnsemble":SousEnsemble, "site":Site, "produit":Produit, "industrie":Industrie,
        "drv":Drv, "agent":Agent, "dep":Dep, "bassin":Bassin, "ville":Ville}
      for name, model in dictModel.items():
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
      setattr(cls, "__indexesPdvs", Pdv.listIndexes())
      setattr(cls, "__structurePdvs", Pdv.listFields())
      if not os.path.isfile("./visioServer/modelStructure/pdvDict.json"):
        with open("./visioServer/modelStructure/pdvDict.json", 'w') as jsonFile:
          json.dump(Pdv.dictValues(), jsonFile, indent = 3)
      with open("./visioServer/modelStructure/pdvDict.json") as jsonFile:
        pdvs = {int(id):value for id, value in json.load(jsonFile).items()}
        setattr(cls, "__pdvs", pdvs)
      return
    if len(model.listFields()) > 1:
      setattr(cls, f"__structure{name.capitalize()}", model.listFields())
    indexes = model.listIndexes()
    if len(indexes) != 0:
      setattr(cls, f"__indexes{name.capitalize()}", indexes)
    setattr(cls, f"__{name}", model.dictValues())

  @classmethod
  def insertModel(cls, data, name, listId=False):
    listAttr = [f"__structure{name.capitalize()}", f"__indexes{name.capitalize()}", f"__{name}"]
    for attr in listAttr:
      if hasattr(cls, attr):
        listIdComputed = listId(data, name) if listId else False
        if attr == f"__{name}" and (isinstance(listIdComputed, list) or isinstance(listIdComputed, set)):
          data[attr[2:]] = {id:value for id, value in getattr(cls, attr).items() if id in listIdComputed}
        else:
          data[attr[2:]] = getattr(cls, attr)
  
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
    listModel = {
      "pdvs":self._computeListPdv, "dashboards":self._computelistdb, "layout":False, "widget":False, "widgetParams":self._computelistWP, "widgetCompute":self._computelistWC,
      "labelForGraph":False, "axisForGraph":False, "params":False, "segmentMarketing":False, "segmentCommercial":False, "enseigne":self._computeFieldPdv, "ensemble":self._computeFieldPdv, "sousEnsemble":self._computeFieldPdv, "site":self._computeFieldPdv, "produit":False, "industrie":False, "drv":self._computeFieldPdv, "agent":self._computeFieldPdv, "dep":self._computeFieldPdv, "bassin":self._computeFieldPdv, "ville":self._computeFieldPdv}
    for name, list in listModel.items():
      self.insertModel(data, name, list)
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

  def _computelistdb(self, data, name):
    levelGeo = data["levelGeo"]
    listId = []
    for level in [levelGeo, self.__levelTrade]:
      while len(level) == 4:
        listId += level[2]
        level = level[3]
    return set(listId)

  def _computelistWP(self, data, name):
    if self.__userGroup == "root": return False
    listId = []
    for db in data["dashboards"].values():
      listId += list(db[3].values())
    return set(listId)

  def _computelistWC(self, data, name):
    if self.__userGroup == "root": return False
    return set([wp[4] for wp in data["widgetParams"].values()])

  def _computeListPdv(self, data, name):
    if self.__userGroup == "root": return False
    self.__pdvSelected = self.__computeListIdPdv(data["geoTree"])
    return self.__pdvSelected

  def __computeListIdPdv(self, geoTree, listId:list = []):
    if isinstance(geoTree, list):
      for subLevel in geoTree[1]:
        self.__computeListIdPdv(subLevel, listId)
    else:
      listId.append(geoTree)
    return listId
  
  def _computeFieldPdv(self, data, name):
    if self.__userGroup == "root":
      if name == "drv":
        data["root"] = {0:""}
      return False
    if self.__userGroup == "agent" and name == "agent":
      del data["drv"]
    if isinstance(self.__pdvSelected[0], int):
      self.__pdvSelected = [data["pdvs"][id] for id in self.__pdvSelected]
    indexField = data["structurePdvs"].index(name)
    return set([line[indexField] for line in self.__pdvSelected])

  def _computeLocalTargetLevel(self, data):
    if self.__userGroup == "root":
      data["structureTargetLevelDrv"] = self.__structureTargetLevelDrv
      data["targetLevelDrv"] = self.__targetLevelDrv
      data["targetLevelAgentP2CD"] = self.__targetLevelAgentP2CD
      data["structureTargetLevelAgentFinition"] = self.__structureTargetLevelAgentFinition
      data["targetLevelAgentFinition"] = self.__targetLevelAgentFinition
    elif self.__userGroup == "drv":
      indexDrv, indexAgent = data["structurePdvs"].index("drv"), data["structurePdvs"].index("agent")
      listAgentId = [line[indexAgent] for line in data["pdvs"].values() if line[indexDrv] == self.__userGeoId]
      data["structureTargetLevelDrv"] = self.__structureTargetLevelDrv
      data["targetLevelDrv"] = {id:level for id, level in self.__targetLevelDrv.items() if id == self.__userGeoId}
      data["targetLevelAgentP2CD"] = {id:value for id, value in self.__targetLevelAgentP2CD.items() if id in listAgentId}
      data["structureTargetLevelAgentFinition"] = self.__structureTargetLevelAgentFinition
      data["targetLevelAgentFinition"] = {id:level for id, level in self.__targetLevelAgentFinition.items() if level[0] == self.__userGeoId}
    elif self.__userGroup == "agent":
      data["structureTargetAgentP2CD"] = self.__structureTargetLevelAgentP2CD
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


  @classmethod
  def getUpdate(cls, userId, userGroup, nature):
    print("query getUpdate", userId, userGroup, nature)
    if nature == "request":
      return {"message":"getUpdate request received"}
    elif nature == "acknowledge":
      return {"message":"getUpdate acknowledge received"}
    else:
      return {"error":f"wrong nature received : {nature}"}

  @classmethod
  def postUpdate(cls, userId, userGroup, data):
    print("query getUpdate", userId, userGroup, data)
    return {"message":"postUpdate received"}