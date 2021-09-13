from ..models import *
import json
from django.conf import settings
from django.forms.models import model_to_dict
from django.db.models.fields.related import ForeignKey
from ..utils import camel
import os
from dotenv import load_dotenv

load_dotenv()
class DataGeneric:
  structure = ['levelName', 'prettyPrint', 'listDashBoards', 'subLevel']
  cacheFile = os.getenv('SALES_DICT')
  testReg = json.loads(os.getenv('REGULAR_MODELS'))
  with open('visioServer/config.json', 'r') as cfgFile:
    config = json.load(cfgFile)
    __salesDict = None

  def _formatObjectName(self, name, modelName):
    if modelName == "bassin":
      return name.replace("Négoce_", "")
    return name

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
  def salesDict(cls):
    if cls.__salesDict: return cls.__salesDict
    if settings.DEBUG:
      try:
        with open(cls.cacheFile, 'r') as jsonFile:
          cls.__salesDict = json.load(jsonFile)
      except:
        print('Formating sales...')
    if not cls.__salesDict:
      cls.__salesDict = cls.__formatSales()
      with open(cls.cacheFile, 'w') as jsonFile:
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
  def _formatPdv(cls):
    listPdv = [model_to_dict(object) for object in Pdv.objects.all()]
    formatedPdvs = {pdv['id']:[value for key, value in pdv.items() if key != 'id'] + [cls.salesDict().get(str(pdv['id']), [])] for pdv in listPdv}
    fields = list(listPdv[0].keys())[1:]
    indexes = []
    for fieldName in fields:
        if type(Pdv._meta.get_field(fieldName)) is ForeignKey:
            indexes.append(fields.index(fieldName))
    fields += ['sales']
    dataPdv = {'fields' : fields, 'indexes': indexes}
    dataPdv.update(formatedPdvs)
    return formatedPdvs, dataPdv

class DataDashboard(DataGeneric):
  levels = None

  def __init__(self):
    self.__dictDashboard = self.__computeDashboards ()

  @property
  def dataQuery(self):
    data = {"structure":DataGeneric.structure}
    formatedPdvs, data['pdv'] = self._formatPdv()
    regularModels = [eval(modelName) for modelName in self.config["regularModels"]]
    data["root"] = {0:""}
    for model in regularModels:
        key = camel(model.__name__)
        data.update({key: {object.id: self._formatObjectName(object.name, key) for object in model.objects.all()}})
    data['geoTree'] = self._buildTree(0, self.config["geoTreeStructure"], formatedPdvs)
    data['tradeTree'] = self._buildTree(0, self.config["tradeTreeStructure"], formatedPdvs)
    if not DataDashboard.levels:
      DataDashboard.levels = DataDashboard._computeLevels(TreeNavigation)
    data['dashboards'] = self.__dictDashboard
    data['levels'] = DataDashboard.levels
    return data

  @classmethod
  def _computeLevels(cls, classObject):
    listLevel = {object.id:object for object in classObject.objects.all()}
    dictLevelWithDashBoard = {}
    for object in listLevel.values():
      dictLevelWithDashBoard[object.id] = list(model_to_dict(object).values())
      del dictLevelWithDashBoard[object.id][0]
      dashBoardTree = DashboardTree.objects.filter(level=object).first()
      dictLevelWithDashBoard[object.id].insert(2, [dashboard.id for dashboard in dashBoardTree.dashboards.all()])
    for level in dictLevelWithDashBoard.values():
      if level[3]:
        dictLevelWithDashBoard[level[3]][3] = level
    level.pop()
    return dictLevelWithDashBoard[1]

  def __computeDashboards(self):
    return {object.id:self.__computeDashboard(object) for object in Dashboard.objects.all()}

  def __computeDashboard(self, object):
    dictDb = model_to_dict(object)
    dictDb["widgetParams"] = [widgetParams.id for widgetParams in dictDb["widgetParams"]]
    del dictDb["id"]
    return dictDb


class Navigation(DataGeneric):
  structure = ['levelName', 'prettyPrint', 'listDashBoards', 'subLevel']
  levels = None

  def __init__(self, userGeoId:int, userGroup:str):
    if not Navigation.levels:
      Navigation.initialiseClass()
    self.__userGeoId = userGeoId
    self.__userGroup = userGroup
    self.__levels = self.__computeLocalLevels(Navigation.levels)
    self.__dictDashboard = self.__computeDashboards ()

  @property
  def dataQuery(self):
    data = {
      "structure":self.structure,
      "levels":self.__levels,
      "dashboards":self.__dictDashboard,
      "geoTree":self.__computeGeoTree()
      }
    self.__createModels(data)
    with open("visioServer/modelStructure/Navigation.json", 'w') as jsonFile:
        json.dump(data, jsonFile)
    return data

  def __createModels(self, data):
    models = list(self.config["navModels"])
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

  def __computeLocalLevels(self, selectedLevel):
    if selectedLevel[0] == self.__userGroup:
      return selectedLevel
    return self.__computeLocalLevels(selectedLevel[3])

  def __computeGeoTree(self):
    """Return a geoTree adapted to the profile of user"""
    if self.__userGroup == "root":
      return Navigation.geoTree
    if self.__userGroup == "drv":
      for drv in Navigation.geoTree[1]:
        if drv[0] == self.__userGeoId:
          return drv
    hierarchy = self.__computeHierarchy()
    drvId = [couple[0] for couple in hierarchy if couple[1] == self.__userGeoId][0]
    for drv in Navigation.geoTree[1]:
        if drv[0] == drvId:
          for agent in drv[1]:
            if agent[0] == self.__userGeoId:
              return agent

  def __computeHierarchy(self) -> list:
    """Hierachy is a list of couples containing drvId dans agentId"""
    hierarchy = []
    for drv in Navigation.geoTree[1]:
      drvId = drv[0]
      for agent in drv[1]:
        hierarchy.append((drvId, agent[0]))
    return hierarchy

  @classmethod
  def __computeLevelName(cls, source:list, levelsName:list=[]):
    levelName = source[1]
    if levelName == "dep":
      return levelsName[1:]
    levelsName.append(levelName)
    return cls.__computeLevelName(source[4], levelsName)



  @classmethod
  def initialiseClass(cls):
    Navigation.levels = Navigation._computeLevels(TreeNavigation)
    formatedPdvs, Navigation.listPdv = cls._formatPdv()
    Navigation.geoTree = cls._buildTree(0, cls.config["geoTreeStructure"], formatedPdvs)
    Navigation.geoTreeStructure = [Navigation.listPdv['fields'][id] for id in cls.config["geoTreeStructure"]]

  def __computeDashboards(self):
    return {object.id:self.__computeDashboard(object) for object in Dashboard.objects.all()}

  def __computeDashboard(self, object):
    dictDb = model_to_dict(object)
    dictDb["widgetParams"] = [widgetParams.id for widgetParams in dictDb["widgetParams"]]
    del dictDb["id"]
    return dictDb

  @classmethod
  def _computeLevels(cls, classObject):
    listLevel = {object.id:object for object in classObject.objects.all()}
    dictLevelWithDashBoard = {}
    for object in listLevel.values():
      dictLevelWithDashBoard[object.id] = list(model_to_dict(object).values())
      del dictLevelWithDashBoard[object.id][0]
      dashBoardTree = DashboardTree.objects.filter(level=object).first()
      dictLevelWithDashBoard[object.id].insert(2, [dashboard.id for dashboard in dashBoardTree.dashboards.all()])
    for level in dictLevelWithDashBoard.values():
      if level[3]:
        dictLevelWithDashBoard[level[3]][3] = level
    level.pop()
    return dictLevelWithDashBoard[1]


