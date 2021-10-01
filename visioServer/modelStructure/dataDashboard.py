from ..models import *
import json
from django.conf import settings
from django.forms.models import model_to_dict
from django.db.models.fields.related import ForeignKey
import datetime
from ..utils import camel
import os
from dotenv import load_dotenv

load_dotenv()

class DataDashboard:
  __structureLevel = ['levelName', 'prettyPrint', 'listDashBoards', 'subLevel']
  __levelGeo = None
  __salesDict = None
  __formatedPdvs = None
  __dataPdvs = None
  __cacheSalesDict = os.getenv('SALES_DICT')
  __structureWidgetParam = None
  __WidgetParamIndexPosition = None
  __structureTarget = None
  __structureTargetLevelDrv = None
  __structureTargetLevelAgentP2CD = None
  __structureTargetLevelAgentFinition = None

  def __init__(self, userGeoId, userGroup, isNotOnServer):
    self.__userGeoId = userGeoId
    self.__userGroup = userGroup
    DataDashboard.isNotOnServer = isNotOnServer
    if not DataDashboard.__levelGeo:
      DataDashboard.__levelGeo = DataDashboard._computeLevels(TreeNavigation, "geo")
      DataDashboard.__levelTrade = DataDashboard._computeLevels(TreeNavigation, "trade")
      DataDashboard.__formatedPdvs, DataDashboard.__dataPdvs = DataDashboard._formatPdv()
      DataDashboard.__geoTreeStructure = json.loads(os.getenv('GEO_TREE_STRUCTURE'))
      DataDashboard.__geoTree = self._buildTree(0, DataDashboard.__geoTreeStructure, DataDashboard.__formatedPdvs)
      DataDashboard.__tradeTreeStructure = json.loads(os.getenv('TRADE_TREE_STRUCTURE'))
      DataDashboard.__tradeTree = self._buildTree(0, DataDashboard.__tradeTreeStructure, DataDashboard.__formatedPdvs)
      DataDashboard.__target = self._computeTarget()
      dictModel = {
        "layout":Layout, "widget":Widget, "widgetCompute":WidgetCompute, "params":ParamVisio,
        "labelForGraph":LabelForGraph, "axisForGraph": AxisForGraph}
      for name, model in dictModel.items():
         DataDashboard.createFromModel(model, name)
      
      DataDashboard.__widgetParam = DataDashboard._computeWidgetParam()
      self._computeTargetLevel()

  @classmethod
  def createFromModel(cls, model, name):
    if len(model.listFields()) > 1:
      setattr(cls, f"__structure{name.capitalize()}", model.listFields())
    indexes = model.listIndexes()
    if len(indexes) != 0: setattr(cls, f"__indexes{name.capitalize()}", indexes)
    setattr(cls, f"__{name}", model.dictValues())

  @classmethod
  def insertModel(cls, data, name):
    listAttr = [f"__structure{name.capitalize()}", f"__indexes{name.capitalize()}", f"__{name}"]
    for attr in listAttr:
      if hasattr(cls, attr):
        data[attr[2:]] = getattr(cls, attr)
  
  @property
  def dataQuery(self):
    levelGeo = self._computeLocalLevels(DataDashboard.__levelGeo, self.__userGroup)
    structureDashboard, dashboards = self._computeLocalDashboards(levelGeo)
    geoTree = self._computeLocalGeoTree()
    pdvs = self._computeLocalPdvs(geoTree)
    data = {
      "structureLevel":DataDashboard.__structureLevel,
      "levelGeo":levelGeo,
      "levelTrade": DataDashboard.__levelTrade,
      "structureDashboard":structureDashboard,
      "indexesDashboard":[1,3],
      "dashboards": dashboards,
      "structureWidgetParam":DataDashboard.__structureWidgetParam,
      "widgetParams":self._computewidgetParams(dashboards),
      "geoTree":geoTree,
      "tradeTree":DataDashboard.__tradeTree,
      "structurePdv":DataDashboard.__dataPdvs["fields"],
      "indexesPdv":DataDashboard.__dataPdvs["indexes"],
      "pdvs": pdvs,
      }
    self._createModelsForGeo(data)
    self._createOtherModels(data)
    data["structureTarget"] = DataDashboard.__structureTarget
    data["target"] = self._computeLocalTarget(pdvs)
    self. _computeLocalTargetLevel(data)
    listModel = ["layout", "widget", "widgetCompute", "labelForGraph", "axisForGraph", "params"]
    for name in listModel:
      self.insertModel(data, name)
    return data

  def _computeLocalLevels(self, originLevel:list, selectedLevel:str):
    if originLevel[0] == selectedLevel:
      return originLevel
    return self._computeLocalLevels(originLevel[3], selectedLevel)

  def _computeLocalDashboards(self, levelGeo:list) -> dict:
    print("_computeLocalDashboards", levelGeo)
    listIdDb = self._computelistDashboardId(levelGeo)
    dictDb = {object.id:self.__computeDashboard(object) for object in Dashboard.objects.all() if object.id in listIdDb}
    structureDashboard, dashboards = [], {}
    for id, db in dictDb.items():
      if not structureDashboard:
        structureDashboard = list(db.keys())
      dashboards[id] = list(db.values())
      listObjWidgetParam = [WidgetParams.objects.get(id = idWP) for idWP in dashboards[id][3]]
      dashboards[id][3] = {object.position:object.id for object in listObjWidgetParam}
    return structureDashboard, dashboards

  def _computelistDashboardId(self, levelGeo):
    listId = []
    for level in [levelGeo, self.__levelTrade]:
      print("_computelistDashboardId", self.__levelTrade)
      while len(level) == 4:
        listId += level[2]
        level = level[3]
    print("_computelistDashboardId", levelGeo, set(listId))
    return set(listId)

  def __computeDashboard(self, object):
    dictDb = model_to_dict(object)
    dictDb["widgetParams"] = [widgetParams.id for widgetParams in dictDb["widgetParams"]]
    del dictDb["id"]
    return dictDb

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

  def _computeLocalPdvs(self, geoTree):
    if self.__userGroup == "root":
      return {key:value for key, value in DataDashboard.__formatedPdvs.items()}
    listId = self.__computeListIdPdv(geoTree)
    return {key:value for key, value in DataDashboard.__formatedPdvs.items() if key in listId}

  def __computeListIdPdv(self, geoTree, listId:list = []):
    if isinstance(geoTree, list):
      for subLevel in geoTree[1]:
        self.__computeListIdPdv(subLevel, listId)
    else:
      listId.append(geoTree)
    return listId

  def _computeLocalTarget(self, pdvs):
    indexPdv = DataDashboard.__structureTarget.index("pdv")
    pdvId = list(pdvs.keys())
    print("pdvId", pdvId)
    print("target pdv keys", [item[indexPdv] for item in DataDashboard.__target.values()])
    return {key:value for key, value in DataDashboard.__target.items() if value[indexPdv] in pdvId}

  def _createModelsForGeo(self, data):
    models = json.loads(os.getenv('GEO_MODELS'))
    if self.__userGroup == "root":
      data["root"] = {0:""}
    else:
      del models[0]
      if self.__userGroup == "drv":
        drvId = data["geoTree"][0]
        data["drv"] = {drvId:Drv.objects.get(id=drvId).name}
      else:
        del models[0]
        agentId = data["geoTree"][0]
        data["agent"] = {agentId:Agent.objects.get(id=agentId).name}
    regularModels = [eval(modelName) for modelName in models]
    dictSelectedId = self.__computeSelectedId(data["geoTree"], models)
    for model in regularModels:
      key = camel(model.__name__)
      if key in dictSelectedId:
         data.update({key: {object.id: self._formatObjectName(object.name, key) for object in model.objects.all() if object.id in dictSelectedId[key]}})
      else:
        data.update({key: {object.id: self._formatObjectName(object.name, key) for object in model.objects.all()}})
    data['ville'] = self._createModelVille(data)

  def _createOtherModels(self, data):
    models = json.loads(os.getenv('REGULAR_MODELS'))
    regularModels = [eval(modelName) for modelName in models]
    for model in regularModels:
        key = camel(model.__name__)
        if getattr(model, "currentYear", False):
          data.update({key: {object.id:object.name for object in model.objects.filter(currentYear=True)}})
        else:
          data.update({key: {object.id:object.name for object in model.objects.all()}})

  def _createModelVille(self, data):
    idVille = data['structurePdv'].index("ville")
    listId = [pdv[idVille] for pdv in data['pdvs'].values()]
    return {object.id:object.name for object in Ville.objects.all() if object.id in listId}
    

  def _formatObjectName(self, name, modelName):
    if modelName == "bassin":
      return name.replace("Négoce_", "")
    return name

  def __computeSelectedId(self, tree, models)->dict:
    """compute ids for object selected"""
    listLevel = [camel(name) for name in models]
    dictSelectedId = {}
    if self.__userGroup != "root":
      currentIds = tree[1]
      for level in listLevel:
        listIds, nextIds = [], []
        if isinstance(currentIds[0], list):
          for listCouple in currentIds:
            listIds.append(listCouple[0])
            nextIds += listCouple[1]
          dictSelectedId[level] = listIds
          currentIds = nextIds
    return dictSelectedId

  def _computewidgetParams(self, dashboards):
    listId = []
    for db in dashboards.values():
      listId += list(db[3].values())
    return {key:value for key, value in DataDashboard.__widgetParam.items() if key in listId}

  def _computeLocalTargetLevel(self, data):
    if self.__userGroup == "root":
      data["structureTargetLevelDrv"] = self.__structureTargetLevelDrv
      data["targetLevelDrv"] = self.__targetLevelDrv
      data["structureTargetAgentP2CD"] = self.__structureTargetLevelAgentP2CD
      data["targetLevelAgentP2CD"] = self.__targetLevelAgentP2CD
      data["structureTargetLevelAgentFinition"] = self.__structureTargetLevelAgentFinition
      data["targetLevelAgentFinition"] = self.__targetLevelAgentFinition
    elif self.__userGroup == "drv":
      listAgentId = [agent.id for agent in Agent.objects.all() if agent.drv.id == self.__userGeoId]
      data["structureTargetLevelDrv"] = self.__structureTargetLevelDrv
      data["targetLevelDrv"] = {id:level for id, level in self.__targetLevelDrv.items() if level[0] == self.__userGeoId}
      data["structureTargetAgentP2CD"] = self.__structureTargetLevelAgentP2CD
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
  def _formatPdv(cls):
    listPdv = [cls.__pdvTransform(pdv) for pdv in Pdv.objects.filter(currentYear=True)]
    formatedPdvs = {pdv['id']:[value for key, value in pdv.items() if key != 'id'] + [cls.computeSalesDict().get(str(pdv['id']), [])] for pdv in listPdv}
    fields = list(listPdv[0].keys())[1:]
    indexes = []
    for fieldName in fields:
      if getattr(Pdv, fieldName, False) and type(Pdv._meta.get_field(fieldName)) is ForeignKey:
        indexes.append(fields.index(fieldName))
    fields += ['sales']
    dataPdv = {'fields' : fields, 'indexes': indexes}
    dataPdv.update(formatedPdvs)
    return formatedPdvs, dataPdv

  @classmethod
  def __pdvTransform(cls, pdv):
    nbVisits = sum([visit.nbVisitCurrentYear for visit in Visit.objects.filter(pdv=pdv)])
    dictPdv = model_to_dict(pdv)
    dictPdv["nbVisits"] = nbVisits
    if isinstance(dictPdv["closedAt"], datetime.datetime):
      dictPdv["closedAt"] = dictPdv["closedAt"].isoformat()
    return dictPdv


  @classmethod
  def computeSalesDict(cls):
    if cls.isNotOnServer and not cls.__salesDict:
      try:
        with open(cls.__cacheSalesDict, 'r') as jsonFile:
          cls.__salesDict = json.load(jsonFile)
      except:
        print('Formating sales...')
    if not cls.__salesDict:
      cls.__salesDict = cls.__formatSales()
      if cls.isNotOnServer:
        with open(cls.__cacheSalesDict, 'w') as jsonFile:
          json.dump(cls.__salesDict, jsonFile)
    return cls.__salesDict

  @classmethod
  def __formatSales(cls):
    sales = Ventes.objects.all()
    salesDict = {}
    for sale in sales:
        id = str(sale.pdv.id)
        if id not in salesDict:
            salesDict[id] = []
        salesDict[id].append([sale.industry.id, sale.product.id, sale.volume])
    return salesDict

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
  def _computeWidgetParam(cls):
    return {object.id:cls.__readWidgetParam(object) for object in WidgetParams.objects.all()}

  @classmethod
  def __readWidgetParam(cls, object):
    if not cls.__structureWidgetParam:
      cls.__structureWidgetParam = list(model_to_dict(object).keys())
      cls.__WidgetParamIndexPosition = cls.__structureWidgetParam.index("position")
      del cls.__structureWidgetParam[cls.__WidgetParamIndexPosition]
      del cls.__structureWidgetParam[0]
    widgetParam = list(model_to_dict(object).values())
    del widgetParam[cls.__WidgetParamIndexPosition]
    del widgetParam[0]
    return widgetParam

  @classmethod
  def _computeTarget(cls):
    return {object.id:cls.__readTarget(object) for object in Ciblage.objects.all()}

  @classmethod
  def __readTarget(cls, object):
    if not cls.__structureTarget:
      cls.__structureTarget = list(model_to_dict(object).keys())
      del cls.__structureTarget[0]
    target = list(model_to_dict(object).values())
    del target[0]
    return target

  @classmethod
  def _computeTargetLevel(cls):
    cls.__targetLevelDrv, cls.__targetLevelAgentP2CD, cls.__targetLevelAgentFinition = {}, {}, {}
    for tlObject in CiblageLevel.objects.all():
      if not cls.__structureTargetLevelDrv:
        cls.__structureTargetLevelDrv = ["drv", "volP2CD", "dnP2CD", "volFinition", "dnFinition"]
        cls.__structureTargetLevelAgentP2CD = ["agent", "volP2CD", "dnP2CD"]
        cls.__structureTargetLevelAgentFinition = ["agentFinition", "volFinition", "dnFinition"]
      if tlObject.drv:
        cls.__targetLevelDrv[tlObject.id] = [tlObject.drv.id, tlObject.volP2CD, tlObject.dnP2CD, tlObject.volFinition, tlObject.dnFinition]
      else:
        if tlObject.volP2CD or tlObject.dnP2CD:
          cls.__targetLevelAgentP2CD[tlObject.id] = [tlObject.agent.id, tlObject.volP2CD, tlObject.dnP2CD]
        if tlObject.volFinition or tlObject.volFinition:
          cls.__targetLevelAgentFinition[tlObject.id] = [tlObject.agent.id, tlObject.volFinition, tlObject.dnFinition]

  @classmethod
  def _createParams(cls):
    return {param.field:param.value for param in ParamVisio.objects.all()}


  