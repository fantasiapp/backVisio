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
  __salesDict = None
  __formatedPdvs = None
  __dataPdvs = None
  __cacheSalesDict = os.getenv('SALES_DICT')
  __structureLayout = None
  __structureWidgetParam = None
  __structureWidgetCompute = None

  def __init__(self, userGeoId, userGroup, isNotOnServer):
    self.__userGeoId = userGeoId
    self.__userGroup = userGroup
    DataDashboard.isNotOnServer = isNotOnServer
    if not DataDashboard.__levelGeo:
      DataDashboard.__levelGeo = DataDashboard._computeLevels(TreeNavigation, "geo")
      DataDashboard.__levelTrade = DataDashboard._computeLevels(TreeNavigation, "trade")
      DataDashboard.__layout = DataDashboard._computeLayout()
      DataDashboard.__widget = DataDashboard._computeWidget()
      DataDashboard.__widgetParam = DataDashboard._computeWidgetParam()
      DataDashboard.__widgetCompute = DataDashboard._computeWidgetCompute()
      DataDashboard.__formatedPdvs, DataDashboard.__dataPdvs = DataDashboard._formatPdv()
      DataDashboard.__geoTreeStructure = json.loads(os.getenv('GEO_TREE_STRUCTURE'))
      DataDashboard.__geoTree = self._buildTree(0, DataDashboard.__geoTreeStructure, DataDashboard.__formatedPdvs)
      DataDashboard.__tradeTreeStructure = json.loads(os.getenv('TRADE_TREE_STRUCTURE'))
      DataDashboard.__tradeTree = self._buildTree(0, DataDashboard.__tradeTreeStructure, DataDashboard.__formatedPdvs)
  
  @property
  def dataQuery(self):
    levelGeo = self._computeLocalLevels(DataDashboard.__levelGeo, self.__userGroup)
    structureDashboard, dashboards = self._computeLocalDashboards(levelGeo)
    geoTree = self._computeLocalGeoTree()
    data = {
      "structureLevel":DataDashboard.__structureLevel,
      "levelGeo":levelGeo,
      "levelTrade":DataDashboard.__levelTrade,
      "structureDashboard":structureDashboard,
      "indexesDashboard":[1,2],
      "dashboards": dashboards,
      "structureLayout":DataDashboard.__structureLayout,
      "layout":DataDashboard.__layout,
      "widget":DataDashboard.__widget,
      "structureWidgetParam":DataDashboard.__structureWidgetParam,
      "widgetParams":self._computewidgetParams(dashboards),
      "structureWidgetCompute":DataDashboard.__structureWidgetCompute,
      "widgetCompute":DataDashboard.__widgetCompute,
      "geoTree":geoTree,
      "tradeTree":DataDashboard.__tradeTree,
      "structurePdv":DataDashboard.__dataPdvs["fields"],
      "indexesPdv":DataDashboard.__dataPdvs["indexes"],
      "pdvs":self._computeLocalPdvs(geoTree)
      }
    self._createModelsForGeo(data)
    self._createOtherModels(data)
    return data

  def _computeLocalLevels(self, originLevel:list, selectedLevel:str):
    if originLevel[0] == selectedLevel:
      return originLevel
    return self._computeLocalLevels(originLevel[3], selectedLevel)

  def _computeLocalDashboards(self, levelGeo:list) -> dict:
    listIdDb = self._computelistDashboardId(levelGeo, [])
    dictDb = {object.id:self.__computeDashboard(object) for object in Dashboard.objects.all() if object.id in listIdDb}
    structureDashboard, dashboards = [], {}
    for id, db in dictDb.items():
      if not structureDashboard:
        structureDashboard = list(db.keys())
      dashboards[id] = list(db.values())
      listObjWidgetParam = [WidgetParams.objects.get(id = idWP) for idWP in dashboards[id][2]]
      dashboards[id][2] = {object.position:object.id for object in listObjWidgetParam}
    return structureDashboard, dashboards

  def _computelistDashboardId(self, levelGeo, listId):
    for id in levelGeo[2]:
      if not id in listId:
        listId.append(id)
    if len(levelGeo) == 4:
      return self._computelistDashboardId(levelGeo[3], listId)
    return listId

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
      listId += list(db[2].values())
    return {key:value for key, value in DataDashboard.__widgetParam.items() if key in listId}

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
    listPdv = [model_to_dict(object) for object in Pdv.objects.all()]
    formatedPdvs = {pdv['id']:[value for key, value in pdv.items() if key != 'id'] + [cls.computeSalesDict().get(str(pdv['id']), [])] for pdv in listPdv}
    fields = list(listPdv[0].keys())[1:]
    indexes = []
    for fieldName in fields:
        if type(Pdv._meta.get_field(fieldName)) is ForeignKey:
            indexes.append(fields.index(fieldName))
    fields += ['sales']
    dataPdv = {'fields' : fields, 'indexes': indexes}
    dataPdv.update(formatedPdvs)
    return formatedPdvs, dataPdv

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
  def _computeLayout(cls):
    return {object.id:cls.__readLayout(object) for object in Layout.objects.all()}

  @classmethod
  def __readLayout(cls, object):
    if not cls.__structureLayout:
      cls.__structureLayout = list(model_to_dict(object).keys())
      del cls.__structureLayout[0]
    layout = list(model_to_dict(object).values())
    del layout[0]
    layout[1] = json.loads(layout[1])
    return layout

  @classmethod
  def _computeWidget(cls):
    return {object.id:object.name for object in Widget.objects.all()}

  @classmethod
  def _computeWidgetParam(cls):
    return {object.id:cls.__readWidgetParam(object) for object in WidgetParams.objects.all()}

  @classmethod
  def __readWidgetParam(cls, object):
    if not cls.__structureWidgetParam:
      cls.__structureWidgetParam = list(model_to_dict(object).keys())
      print(cls.__structureWidgetParam )
      del cls.__structureWidgetParam[0]
      del cls.__structureWidgetParam[2]
    widgetParam = list(model_to_dict(object).values())
    del widgetParam[0]
    del widgetParam[2]
    return widgetParam

  @classmethod
  def _computeWidgetCompute(cls):
    return {object.id:cls.__readWidgetCompute(object) for object in WidgetCompute.objects.all()}

  @classmethod
  def __readWidgetCompute(cls, object):
    if not cls.__structureWidgetCompute:
      cls.__structureWidgetCompute = list(model_to_dict(object).keys())
      del cls.__structureWidgetCompute[0]
    widgetCompute = list(model_to_dict(object).values())
    del widgetCompute[0]
    widgetCompute[3] = json.loads(widgetCompute[3])
    widgetCompute[4] = json.loads(widgetCompute[4])
    return widgetCompute

  