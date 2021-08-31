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
  def _buildTree(cls, name, steps:list, pdvs:list):
    if not steps:
        return [name, list(pdvs.keys())]
    nextKey = steps[0]
    children = [cls._buildTree(name, steps[1:], associatedPdvs) for name, associatedPdvs in cls._diceByKey(nextKey, pdvs).items()]
    return [name, children]

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
  def _diceByKey(cls, index, pdvs:list):
    dicedBykey = {}
    for id, pdv in pdvs.items():
        if pdv[index] not in dicedBykey:
            dicedBykey[pdv[index]] = {}
        dicedBykey[pdv[index]][id] = pdv
    return dicedBykey

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

  def __init__(self):
    self.__levels = self.__computeLevels()
    self.__dictDashboard = self.__computeDashboards ()

  @property
  def dataQuery(self):
    data = {"structure":self.structure, "levels":self.__levels, "dashboards":self.__dictDashboard}
    regularModels = [eval(modelName) for modelName in self.config["navModels"]]
    for model in regularModels:
        data.update({camel(model.__name__): {object.id: object.name for object in model.objects.all()}})
    formatedPdvs, listPdv = self._formatPdv()
    data['geoTree'] = self._buildTree('root', self.config["geoTreeStructure"], formatedPdvs)
    data['geoTreeStructure'] = [listPdv['fields'][id] for id in self.config["geoTreeStructure"]]
    with open("visioServer/modelStructure/Navigation.json", 'w') as jsonFile:
        json.dump(data, jsonFile)
    return data

  def __computeLevels(self):
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


