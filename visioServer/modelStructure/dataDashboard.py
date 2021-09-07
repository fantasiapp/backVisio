from ..models import *
import json
from django.conf import settings
from django.forms.models import model_to_dict
from django.db.models.fields.related import ForeignKey
from ..utils import camel

class DataGeneric:
  cacheFile = 'visioServer/modelStructure/salesDict.json'
  with open('visioServer/config.json', 'r') as cfgFile:
    config = json.load(cfgFile)
    __salesDict = None

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
      except: pass
    if not cls.__salesDict:
      cls.__salesDict = cls.__formatSales()
      with open(cls.cacheFile, 'w') as jsonFile:
        json.dump(cls.__salesDict, jsonFile)
    return cls.__salesDict

  @classmethod
  def __formatSales(cls):
    print('Formating sales...')
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

  def __init__(self):
    pass

  @property
  def dataQuery(self):
    data = {}
    formatedPdvs, data['pdv'] = self._formatPdv()
    regularModels = [eval(modelName) for modelName in self.config["regularModels"]]
    for model in regularModels:
        data.update({camel(model.__name__): {object.id: object.name for object in model.objects.all()}})
    data['geoTree'] = self._buildTree('root', self.config["geoTreeStructure"], formatedPdvs)
    data['tradeTree'] = self._buildTree('root', self.config["tradeTreeStructure"], formatedPdvs)
    data['geoTreeStructure'] = [data['pdv']['fields'][id] for id in self.config["geoTreeStructure"]]
    data['tradeTreeStructure'] = [data['pdv']['fields'][id] for id in self.config["tradeTreeStructure"]]
    jsonData = {"geoTree":data['geoTree'], 'geoTreeStructure':data['geoTreeStructure']}
    with open("visioServer/modelStructure/Dashboards.json", 'w') as jsonFile:
        json.dump(jsonData, jsonFile)
    return data


class Navigation(DataGeneric):
  structure = ['id', 'levelName', 'prettyPrint', 'listDashBoards', 'subLevel']
  levels = None

  def __init__(self, userGeoId:int, userGroup:str):
    if not Navigation.levels:
      Navigation.__initialiseClass()
    self.__userGeoId = userGeoId
    self.__userGroup = userGroup
    self.__levels = self.__computeLocalLevels(Navigation.levels)
    self.__dictDashboard = self.__computeDashboards ()

  @property
  def dataQuery(self):
    data = {"structure":self.structure, "levels":self.__levels, "dashboards":self.__dictDashboard}
    regularModels = [eval(modelName) for modelName in self.config["navModels"]]
    for model in regularModels:
        data.update({camel(model.__name__): {object.id: object.name for object in model.objects.all()}})
    data['geoTree'] = self.__computeGeoTree()
    data['geoTreeStructure'] = self.__computeGeoTreeStructure()
    with open("visioServer/modelStructure/Navigation.json", 'w') as jsonFile:
        json.dump(data, jsonFile)
    return data

  def __computeLocalLevels(self, selectedLevel):
    if selectedLevel[1] == self.__userGroup:
      return selectedLevel
    return self.__computeLocalLevels(selectedLevel[4])

  def __computeGeoTree(self):
    """Return a geoTree adapted to the profile of user"""
    if self.__userGroup == "root":
      return Navigation.geoTree
    if self.__userGroup == "drv":
      for drv in Navigation.geoTree[1]:
        if drv[0] == self.__userGeoId:
          return ["drv", drv[1]]
    hierarchy = self.__computeHierarchy()
    drvId = [couple[0] for couple in hierarchy if couple[1] == self.__userGeoId][0]
    for drv in Navigation.geoTree[1]:
        if drv[0] == drvId:
          for agent in drv[1]:
            if agent[0] == self.__userGeoId:
              return ["agent", agent[1]]

  def __computeGeoTreeStructure(self):
    if self.__userGroup in Navigation.geoTreeStructure:
      index = Navigation.geoTreeStructure.index(self.__userGroup)
      return Navigation.geoTreeStructure[index + 1:]
    return Navigation.geoTreeStructure

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
  def __initialiseClass(cls):
    Navigation.levels = Navigation.__computeLevels()
    formatedPdvs, Navigation.listPdv = cls._formatPdv()
    Navigation.geoTree = cls._buildTree('root', cls.config["geoTreeStructure"], formatedPdvs)
    Navigation.geoTreeStructure = [Navigation.listPdv['fields'][id] for id in cls.config["geoTreeStructure"]]

  @classmethod
  def __computeLevels(cls):
    listLevel = {object.id:object for object in TreeNavigation.objects.all()}
    dictLevelWithDashBoard = {}
    for object in listLevel.values():
      dictLevelWithDashBoard[object.id] = list(model_to_dict(object).values())
      dashBoardTree = DashboardTree.objects.filter(level=object).first()
      dictLevelWithDashBoard[object.id].insert(3, [dashboard.id for dashboard in dashBoardTree.dashboards.all()])
    for level in dictLevelWithDashBoard.values():
      if level[4]:
        dictLevelWithDashBoard[level[4]][4] = level
    level.pop()
    return dictLevelWithDashBoard[1]

  def __computeDashboards(self):
    return {object.id:self.__computeDashboard(object) for object in Dashboard.objects.all()}

  def __computeDashboard(self, object):
    dictDb = model_to_dict(object)
    del dictDb["id"]
    return dictDb


