from django.db import models
from django.contrib.auth.models import User
from datetime import date
import json
# from django.db.models.fields import Field
import datetime
from django.db.models.lookups import IntegerFieldFloatRounding
from django.utils import timezone
import inspect

# from django.forms.models import model_to_dict

class CommonModel(models.Model):
  """jsonFields tells which field are to be loaded."""
  jsonFields = []
  readingData = {}

  class Meta:
    abstract = True

  @classmethod
  def listFields(cls):
    return [field.name for field in cls._meta.fields if field.name != "currentYear"][1:]

  @classmethod
  def listIndexes(cls):
    listName = cls.listFields()
    listNameF = [name for name in listName if getattr(cls, name, False) and (isinstance(cls._meta.get_field(name), models.ForeignKey) or isinstance(cls._meta.get_field(name), models.ManyToManyField))]
    return [listName.index(name) for name in listNameF]

  @classmethod
  def dictValues(cls, currentYear=True):
    length = len(cls.listFields()) == 1
    if getattr(cls, "currentYear", False):
      result = {instance.id:instance.listValues[0] if length else instance.listValues for instance in cls.objects.filter(currentYear=currentYear)}
      return result
    if currentYear == True:
      return {instance.id:instance.listValues[0] if length else instance.listValues for instance in cls.objects.all()}
    return False

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

  @property
  def listValues(self):
    listFields = self.listFields()
    listRow = [getattr(self, field, False) for field in listFields]
    if "date" in listFields:
      indexDate = listFields.index("date")
      listRow[indexDate] = listRow[indexDate].timestamp() if listRow[indexDate] else None
    for index in self.listIndexes():
      if isinstance(self._meta.get_field(listFields[index]), models.ManyToManyField):
        listRow[index] = [element.id for element in listRow[index].all()]
      elif listRow[index]:
        listRow[index] = listRow[index].id
    if self.jsonFields:
      for jsonField in self.jsonFields:
        index = self.listFields().index(jsonField)
        listRow[index] = json.loads(listRow[index])
    return listRow

  @classmethod
  def computeListId(cls, dataDashboard, data):
    name = cls.readingData["name"] if "name" in cls.readingData else None
    if dataDashboard.userGroup == "root":
      return False
    if "pdvFiltered" in cls.readingData:
      indexField = data["structurePdvs"].index(name)
      return set([line[indexField] for line in dataDashboard.dictLocalPdv[dataDashboard.currentYear].values()])
    return False

  @classmethod
  def computeTableClass(cls):
    listClass= ([cls for cls in CommonModel.__subclasses__() if "nature" in cls.readingData and cls.readingData["nature"] == "normal"])
    return list(dict(sorted({cls.readingData["position"]:(cls.readingData["name"], cls) for cls in listClass}.items())).values())

  @classmethod
  def getDataFromDict(cls, field, data):
    if data:
      structureData = cls.listFields()
      try:
        indexField = structureData.index(field)
      except ValueError:
        return False
      if len(data) > indexField:
        return data[indexField]
    return False

  def createKwargsToSave(self, valueReceived, date=timezone.now(), update=True):
    kwargs = {}
    for fieldName in self.listFields():
      if fieldName == "date":
        kwargs[fieldName] = date
      else:
        newValue = self.getDataFromDict(fieldName, valueReceived)
        test = True
        if update:
          if getattr(self, fieldName, None) != None:
            if isinstance(self._meta.get_field(fieldName), models.ForeignKey):
              test = newValue != getattr(self, fieldName).id
            else:
              test = newValue != getattr(self, fieldName)
          else:
            test = False
        if test:
          kwargs[fieldName] = newValue
    return kwargs

  def update(self, valueReceived, now):
    kwargs = self.createKwargsToSave(valueReceived, now)
    if kwargs:
      for fieldName, value in kwargs.items():
        if value != None and value != getattr(self, fieldName):
          setattr(self, fieldName, value)
      self.save()
      return self.listValues
    return False
      
# Information Params
class ParamVisio(CommonModel):
  field = models.CharField(max_length=64, unique=True, blank=False)
  prettyPrint = models.CharField(max_length=64, unique=False, blank=False, default=None)
  fvalue = models.CharField(max_length=64, unique=False, blank=False)
  typeValue = models.CharField(max_length=64, unique=False, blank=False)
  readingData = {"nature":"normal", "position":6, "name":"params"}

  @classmethod
  def listFields(cls):
    return ["value"]

  @classmethod
  def listIndexes(cls):
    return []

  @classmethod
  def dictValues(cls):
    return {param.field:param.value for param in cls.objects.all()}

  @classmethod
  def getValue(cls, field):
    param = cls.objects.filter(field=field)
    if param: return param[0].value
    return False

  @property
  def value(self):
    if self.typeValue == "int":
      return int(self.fvalue)
    elif self.typeValue == "float":
      return float(self.fvalue)
    elif self.typeValue == "bool":
      return True
    return self.fvalue
    

class Drv(CommonModel):
  name = models.CharField('drv', max_length=16, unique=False)
  currentYear = models.BooleanField("Année courante", default=True)
  readingData = {"nature":"normal", "position":17, "name":"drv", "pdvFiltered":True}

  class Meta:
    verbose_name = "DRV"

  def __str__(self) ->str:
    return self.name

class Agent(CommonModel):
  name = models.CharField('agent', max_length=64, unique=False)
  currentYear = models.BooleanField("Année courante", default=True)
  readingData = {"nature":"normal", "position":18, "name":"agent", "pdvFiltered":True}

  class Meta:
    verbose_name = "Secteur"

  def __str__(self) ->str:
    return self.name

class AgentFinitions(CommonModel):
  name = models.CharField('agent_finitions', max_length=64, unique=False)
  drv = models.ForeignKey('drv', on_delete=models.DO_NOTHING, blank=False, default=None)
  ratioTargetedVisit = models.FloatField('Ratio des visites ciblées', unique=False, blank=False, default=0.3)
  TargetedNbVisit = models.IntegerField('Ratio des visites ciblées', unique=False, blank=False, default=800)
  currentYear = models.BooleanField("Année courante", default=True)
  readingData = {"nature":"normal", "position":19, "name":"agentFinitions", "pdvFiltered":True}

  class Meta:
    verbose_name = "Agent Finitions"

  def __str__(self) ->str:
    return self.name

class Dep(CommonModel):
  name = models.CharField('dep', max_length=2, unique=False)
  currentYear = models.BooleanField("Année courante", default=True)
  readingData = {"nature":"normal", "position":20, "name":"dep", "pdvFiltered":True}

  class Meta:
    verbose_name = "Département"

  def __str__(self) ->str:
    return self.name

class Bassin(CommonModel):
  name = models.CharField('bassin', max_length=64, unique=False)
  currentYear = models.BooleanField("Année courante", default=True)
  readingData = {"nature":"normal", "position":21, "name":"bassin", "pdvFiltered":True}

  class Meta:
    verbose_name = "Bassin"

  def __str__(self) ->str:
    return self.name

  @property
  def listValues(self):
    return [bassin.replace("Négoce_", "") for bassin in super().listValues]

class Ville(CommonModel):
  name = models.CharField('ville', max_length=128, unique=True)
  readingData = {"nature":"normal", "position":22, "name":"ville", "pdvFiltered":True}

  class Meta:
    verbose_name = "Ville"

  def __str__(self) ->str:
    return self.name

class SegmentMarketing(CommonModel):
  name = models.CharField('segment_marketing', max_length=32, unique=False)
  currentYear = models.BooleanField("Année courante", default=True)
  readingData = {"nature":"normal", "position":9, "name":"segmentMarketing"}

  class Meta:
    verbose_name = "Segment Marketing"

  def __str__(self) ->str:
    return self.name

class SegmentCommercial(CommonModel):
  name = models.CharField('segment_commercial', max_length=16, unique=False)
  currentYear = models.BooleanField("Année courante", default=True)
  readingData = {"nature":"normal", "position":10, "name":"segmentCommercial"}

  class Meta:
    verbose_name = "Segment Commercial"

  def __str__(self) ->str:
    return self.name

class Enseigne(CommonModel):
  name = models.CharField('name', max_length=64, unique=False, blank=False, default="Inconnu")
  currentYear = models.BooleanField("Année courante", default=True)
  readingData = {"nature":"normal", "position":11, "name":"enseigne", "pdvFiltered":True}

  class Meta:
    verbose_name = "Enseigne"

  def __str__(self) ->str:
    return self.name

class Ensemble(CommonModel):
  name = models.CharField('name', max_length=64, unique=False, blank=False, default="Inconnu")
  currentYear = models.BooleanField("Année courante", default=True)
  readingData = {"nature":"normal", "position":12, "name":"ensemble", "pdvFiltered":True}

  class Meta:
    verbose_name = "Ensemble"

  def __str__(self) ->str:
    return self.name

class SousEnsemble(CommonModel):
  name = models.CharField('name', max_length=64, unique=False, blank=False, default="Inconnu")
  currentYear = models.BooleanField("Année courante", default=True)
  readingData = {"nature":"normal", "position":13, "name":"sousEnsemble", "pdvFiltered":True}

  class Meta:
    verbose_name = "Sous-Ensemble"

  def __str__(self) ->str:
    return self.name

class Site(CommonModel):
  name = models.CharField('name', max_length=64, unique=False, blank=False, default="Inconnu")
  currentYear = models.BooleanField("Année courante", default=True)
  readingData = {"nature":"normal", "position":14, "name":"site", "pdvFiltered":True}

  class Meta:
    verbose_name = "Site"

  def __str__(self) ->str:
    return self.name

class Pdv(CommonModel):
  code = models.CharField('PDV code', max_length=10, blank=False, default="Inconnu")
  name = models.CharField('PDV', max_length=64, blank=False, default="Inconnu")
  drv = models.ForeignKey('drv', verbose_name='Région', on_delete=models.PROTECT,  blank=False)
  agent = models.ForeignKey('agent', verbose_name='Secteur', on_delete=models.PROTECT, blank=False)
  agentFinitions = models.ForeignKey('agentFinitions', verbose_name='Secteur Finition', on_delete=models.DO_NOTHING, null=True, default=None)
  dep = models.ForeignKey("dep", verbose_name='Département', on_delete=models.PROTECT, blank=False)
  bassin = models.ForeignKey("bassin", verbose_name='Bassin', on_delete=models.PROTECT, blank=False)
  ville = models.ForeignKey("ville", on_delete=models.PROTECT, blank=False)
  latitude = models.FloatField('Latitude', unique=False, blank=False, default=0.0)
  longitude = models.FloatField('Longitude', unique=False, blank=False, default=0.0)
  segmentCommercial = models.ForeignKey("segmentCommercial", on_delete=models.PROTECT, blank=False, default=1)
  segmentMarketing = models.ForeignKey("segmentMarketing", on_delete=models.PROTECT, blank=False, default=1)
  enseigne = models.ForeignKey('Enseigne', verbose_name='Enseigne', on_delete=models.PROTECT, blank=False, default=7)
  ensemble = models.ForeignKey('Ensemble', verbose_name='Ensemble', on_delete=models.PROTECT, blank=False, default=43)
  sousEnsemble = models.ForeignKey('SousEnsemble', verbose_name='Sous-Ensemble', on_delete=models.PROTECT, blank=False, default=1)
  site = models.ForeignKey('site', on_delete=models.PROTECT, blank=False, default=1)
  available = models.BooleanField(default=True)
  sale = models.BooleanField("Ne vend pas de plaque", default=True)
  redistributed = models.BooleanField("Redistribué", default=True)
  redistributedFinitions = models.BooleanField("redistribué Enduit", default=True)
  pointFeu = models.BooleanField('Point Feu', default=False)
  onlySiniat = models.BooleanField('100% Siniat', default=False)
  closedAt = models.DateTimeField('Date de Fermeture', blank=True, null=True, default=None)
  currentYear = models.BooleanField("Année courante", default=True)
  readingData = {"nature":"normal", "position":0, "name":"pdvs"}

  def __str__(self) ->str: return self.name + " " + self.code

  @classmethod
  def listFields(cls):
    return super().listFields() + ["nbVisits", "target", "sales"]

  @classmethod
  def dictValues(cls, currentYear=True):
    indexSale = cls.listFields().index("sale")
    return {id:value for id, value in super().dictValues(currentYear=currentYear).items() if value[indexSale]}

  @classmethod
  def computeListId(cls, dataDashBoard, data):
    return list(dataDashBoard.dictLocalPdv[dataDashBoard.currentYear].keys()) if dataDashBoard.userGroup != "root" else False

  @property
  def listValues(self):
    lv, lf = super().listValues, self.listFields()
    idDat, idNbV, idTar, idSal = lf.index("closedAt"), lf.index("nbVisits"), lf.index("target"), lf.index("sales")
    if isinstance(lv[idDat], datetime.datetime):
      lv[idDat] = lv[idDat].isoformat()
    lv[idNbV] = sum([visit.nbVisitCurrentYear for visit in Visit.objects.filter(pdv=self)])
    target = Target.objects.filter(pdv = self)
    if target:
      lv[idTar] = target[0].listValues
    lv[idSal] = [vente.listValues for vente in Sales.objects.filter(pdv=self)]
    return lv

  def update(self, valueReceived, now):
    super().update(valueReceived, now)
    self.__updateTarget(valueReceived, now)
    for saleReceived in self.getDataFromDict("sales", valueReceived):
      self.__updateSale(saleReceived, now)
    return self.listValues

  def __updateTarget(self, valueReceived, now):
    targetReceived = self.getDataFromDict("target", valueReceived)
    targetObject = Target.objects.filter(pdv=self)
    if targetReceived:
      if targetObject:
        targetObject[0].update(targetReceived, now)
      else:
        Target.createFromList(targetReceived, self, now)

  def __updateSale(self, saleReceived, now):
    industryId = Sales.getDataFromDict("industry", saleReceived)
    productId = Sales.getDataFromDict("product", saleReceived)
    volume = Sales.getDataFromDict("volume", saleReceived)
    sale = Sales.objects.filter(pdv=self, industry=industryId, product=productId)
    if sale:
      if abs(volume - sale[0].volume) > 1:
        sale[0].update(saleReceived, now) if volume else sale[0].delete()
    elif volume:
      Sales.objects.create(date=now, pdv=self, industry=Industry.objects.get(id=industryId), product=Product.objects.get(id=productId), volume=volume)

class Visit(CommonModel):
  date = models.DateField(verbose_name="Mois des visites", default=date.today)
  nbVisit = models.IntegerField(verbose_name="Nombre de visites", blank=False, default=1)
  pdv = models.ForeignKey("PDV", on_delete=models.CASCADE, blank=False, null=False, default=1)
  currentYear = None

  class Meta:
    verbose_name = "Visites Mensuels"

  @property
  def nbVisitCurrentYear(self):
    if not Visit.currentYear:
      currentYear = ParamVisio.objects.filter(field="currentYear")
      Visit.currentYear = currentYear[0].value if currentYear else None
    if self.date.year == Visit.currentYear:
      return self.nbVisit
    return 0

  def __str__(self) ->str:
    return self.date.strftime("%Y-%m") + " " + self.pdv.code

  @classmethod
  def listFields(cls):
      listFields = super().listFields()
      del listFields["pdv"]
      return listFields

 #Modèles pour l'AD

class Product(CommonModel):
  name = models.CharField('name', max_length=32, unique=True, blank=False, default="Inconnu")
  readingData = {"nature":"normal", "position":15, "name":"product"}

  class Meta:
    verbose_name = "Produit"

  def __str__(self) ->str:
    return self.name

class Industry(CommonModel):
  name = models.CharField('name', max_length=32, unique=True, blank=False, default="Inconnu")
  readingData = {"nature":"normal", "position":16, "name":"industry"}

  class Meta:
    verbose_name = "Industrie"

  def __str__(self) ->str:
    return self.name

class Sales(CommonModel):
  date = models.DateTimeField('Date de Saisie', blank=True, null=True, default=None)
  pdv = models.ForeignKey("PDV", on_delete=models.CASCADE, blank=False, default=1)
  industry = models.ForeignKey("Industry", on_delete=models.CASCADE, blank=False, default=17)
  product = models.ForeignKey("Product", on_delete=models.CASCADE, blank=False, default=6)
  volume = models.FloatField('Volume', unique=False, blank=True, default=0.0)
  currentYear = models.BooleanField("Année courante", default=True)

  salesDict = None
  isNotOnServer = False
  cacheSalesDict = None

  class Meta:
    verbose_name = "Ventes"
    unique_together = ('pdv', 'industry', 'product')

  def __str__(self) ->str:
    return str(self.pdv) + " " + str(self.industry) + " " + str(self.product)

  @classmethod
  def listFields(cls):
    lf = super().listFields()
    del lf[1]
    return lf

class TreeNavigation(CommonModel):
  geoOrTrade = models.CharField(max_length=6, unique=False, blank=False, default="Geo")
  levelName = models.CharField(max_length=32, unique=False, blank=False, default=None)
  prettyPrint = models.CharField(max_length=32, unique=False, blank=False, default=None)
  listDashboards = models.ManyToManyField('Dashboard', default = None)
  subLevel = models.ForeignKey('self', on_delete=models.DO_NOTHING, null=True, default=None)

  @classmethod
  def listFields(cls):
    lf = super().listFields()
    del lf[0]
    lf.insert(2, "listDashboards")
    return lf

  @classmethod
  def removeDashboards(cls, level, group, geoOrTrade):
    listFields = cls.listFields()
    indexDb = listFields.index("listDashboards")
    indexSubLevel = listFields.index("subLevel")
    listDbName = ["Synthèse P2CD", "Synthèse Enduit"]
    if geoOrTrade == "geo":
      listDbName = ["PdM Enduit Simulation"] if group == "agent" else ["PdM P2CD Simulation", "DN P2CD Simulation"]
    listDb = [Dashboard.objects.get(name=name, geoOrTrade=geoOrTrade).id for name in listDbName]
    listDb.sort(reverse=True)
    while True:
      for id in listDb:
        if level and id in level[indexDb]:
          idToRemove = level[indexDb].index(id)
          del level[indexDb][idToRemove]
      if level:
        level = level[indexSubLevel]
      else:
        return

  @property
  def listValues(self):
    lv = super().listValues
    index = self.getDataFromDict("subLevel", lv)
    if index:
      indexSubLevel = self.listFields().index("subLevel")
      lv[indexSubLevel] = TreeNavigation.objects.get(id=index).listValues
    return lv

class Layout(CommonModel):
  jsonFields = ["template"]
  name = models.CharField(max_length=64, unique=True, blank=False, default=None)
  template = models.CharField(max_length=2048, unique=False, blank=False, default=None)
  readingData = {"nature":"normal", "position":2, "name":"layout"}

class Widget(CommonModel):
  name = models.CharField(max_length=32, unique=True, blank=False, default=None)
  readingData = {"nature":"normal", "position":3, "name":"widget"}
  
class WidgetParams(CommonModel):
  jsonFields = ["subTitle"]
  title = models.CharField(max_length=128, unique=False, blank=False, default=None)
  subTitle = models.CharField(max_length=2048, unique=False, blank=False, default=None)
  position = models.CharField(max_length=1, unique=False, blank=False, default=None)
  unity = models.CharField("Unité", max_length=32, unique=False, blank=False, default=None)
  widget = models.ForeignKey('Widget', on_delete=models.DO_NOTHING, blank=False, null=False, default=None)
  widgetCompute = models.ForeignKey("WidgetCompute", on_delete=models.DO_NOTHING, blank=False, default=None)
  readingData = {"nature":"normal", "position":4, "name":"widgetParams"}

  @classmethod
  def listFields(cls): return ["title", "subTitle", "unity", "widget", "widgetCompute"]

  @classmethod
  def computeListId(cls, dataDashboard, data):
    if dataDashboard.userGroup == "root": return False
    listId = []
    for db in data["dashboards"].values():
      listId += list(db[3].values())
    return set(listId)


class WidgetCompute(CommonModel):
  jsonFields = ["groupAxis1", "groupAxis2"]
  axis1 = models.CharField("Axe 1", max_length=32, unique=False, blank=False, default=None)
  axis2 = models.CharField("Axe 2", max_length=32, unique=False, blank=False, default=None)
  indicator = models.CharField("Indicateur", max_length=32, unique=False, blank=False, default=None)
  groupAxis1 = models.CharField("Filtre Axe 1", max_length=4096, unique=False, blank=False, default=None)
  groupAxis2 = models.CharField("Filtre Axe 2", max_length=4096, unique=False, blank=False, default=None)
  percent = models.CharField("Pourcentage", max_length=32, unique=False, blank=False, default="no")
  readingData = {"nature":"normal", "position":5, "name":"widgetCompute"}

  @classmethod
  def computeListId(cls, dataDashboard, data):
    if dataDashboard.userGroup == "root": return False
    return set([wp[4] for wp in data["widgetParams"].values()])


class Dashboard(CommonModel):
  jsonFields = ["comment"]
  name = models.CharField(max_length=64, unique=False, blank=False, default=None)
  geoOrTrade = models.CharField(max_length=6, blank=False, default="geo")
  layout = models.ForeignKey('Layout', on_delete=models.PROTECT, blank=False, default=1)
  comment = models.CharField(max_length=2048, unique=False, blank=False, default=None)
  widgetParams = models.ManyToManyField("WidgetParams")
  readingData = {"nature":"normal", "position":1, "name":"dashboards"}

  @classmethod
  def listFields(cls): return ["name", "layout", "comment", "widgetParams"]

  @classmethod
  def computeListId(cls, dataDashboard, data):
    listId = []
    listFields = TreeNavigation.listFields()
    indexDb = listFields.index("listDashboards")
    indexSubLevel = listFields.index("subLevel")
    for level in [data["levelGeo"], data["levelTrade"]]:
      while level[indexSubLevel]:
        listId += level[indexDb]
        level = level[indexSubLevel]
    return set(listId)

  @property
  def listValues(self):
      lv = super().listValues
      listObjWidgetParam = [WidgetParams.objects.get(id = wp.id) for wp in self.widgetParams.all()]
      indexWP = self.listFields().index("widgetParams")
      lv[indexWP] = {object.position:object.id for object in listObjWidgetParam}
      return lv

class LabelForGraph(CommonModel):
  axisType = models.CharField(max_length=32, unique=False, blank=False, default=None)
  label = models.CharField(max_length=32, unique=False, blank=False, default=None)
  color = models.CharField(max_length=32, unique=False, blank=False, default=None)
  readingData = {"nature":"normal", "position":7, "name":"labelForGraph"}

  def __str__(self) ->str:
    return "LabelForGraph " + str(self.axisType) + " " + str(self.label) + " " + str(self.color)

class AxisForGraph(CommonModel):
  name = models.CharField(max_length=32, unique=False, blank=False, default=None)
  labels = models.ManyToManyField("LabelForGraph")
  readingData = {"nature":"normal", "position":8, "name":"axisForGraph"}

  class Meta:
    verbose_name = "Axes pour les graphiques"

  @classmethod
  def listFields(cls): return ["name", "labels"]
  
  def __str__(self) ->str:
    return "AxisForGraph " + str(self.name)


# Informations complémentaire pour les users profile

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.DO_NOTHING)
    idGeo = models.IntegerField(blank=True, default=None)
    lastUpdate = models.DateTimeField('Dernière mise à jour', blank=True, null=True, default=None)

# Information target

class Target(CommonModel):
  date = models.DateTimeField('Date de Saisie', blank=True, null=True, default=None)
  pdv = models.ForeignKey("PDV", on_delete=models.CASCADE, blank=False, default=1)
  redistributed = models.BooleanField("Redistribué", default=True)
  redistributedFinitions = models.BooleanField("Redistribué Enduit", default=True)
  sale = models.BooleanField("Ne vend pas de plaque", default=True)
  targetP2CD = models.FloatField('Cible P2CD', unique=False, blank=True, default=0.0)
  targetFinitions = models.BooleanField('Cible Finitions', unique=False, blank=False, default=False)
  GREEN = 'g'
  ORANGE = 'o'
  RED = 'r'
  COLORS_GREEN_LIGHT_CHOICES = [(GREEN, 'vert'), (ORANGE,'orange'), (RED, 'rouge')] 
  greenLight = models.CharField("Feu Ciblage P2CD", max_length=1, choices=COLORS_GREEN_LIGHT_CHOICES, blank=True, default=None)
  commentTargetP2CD = models.TextField("Commentaires ciblage P2CD", blank=True, default=None)
  bassin = models.CharField(max_length=64, unique=False, blank=True, default="")

  @classmethod
  def listFields(cls):
    lf = super().listFields()
    del lf[lf.index("pdv")]
    return lf

  @classmethod
  def createFromList(cls, data, pdv, now):
    flagSave = False
    kwargs = {"pdv":pdv}
    for fieldName in cls.listFields():
      if fieldName == "date":
        kwargs["date"] = now
      else:
        kwargs[fieldName] = cls.getDataFromDict(fieldName, data)
    try:
      cls.objects.create(**kwargs)
      flagSave = True
    except:
      pass
    return flagSave

class TargetLevel(CommonModel):
  date = models.DateTimeField('Date de Saisie', blank=True, null=True, default=None)
  agent = models.ForeignKey('Agent', on_delete=models.DO_NOTHING, blank=True, null=True, default=None)
  agentFinitions = models.ForeignKey('AgentFinitions', on_delete=models.DO_NOTHING, blank=True, null=True, default=None)
  drv = models.ForeignKey('Drv', on_delete=models.DO_NOTHING, blank=True, null=True, default=None)
  vol = models.FloatField('Cible visée en Volume P2CD', unique=False, blank=False, default=0.0)
  dn = models.IntegerField('Cible visée en dn P2CD', unique=False, blank=False, default=0)
  currentYear = models.BooleanField("Année courante", default=True)

  def createKwargsToSave(self, valueReceived, date=timezone.now(), update=True):
    listFields = self.listFields()
    valueReceived = [date, self.agent, self.agentFinitions, self.drv] + valueReceived
    complete, result = {listFields[index]:valueReceived[index] for index in range(len(listFields))}, {}
    for field, value in complete.items():
      if value != getattr(self, field):
        result[field] = value
    return result if len(result) > 1 else {}

  def update(self, listTargetLevel, now):
    result = super().update(listTargetLevel, now)
    if result:
      listFields = self.listFields()
      for field in ["drv", "agentFinitions", "agent"]:
        index = listFields.index(field)
        del result[index]
    return result
    

class LogUpdate(models.Model):
  date = models.DateTimeField('Date de Reception', blank=True, null=True, default=None)
  user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
  data = models.TextField("Json des updates reçus", blank=True, default="")

class LogClient(CommonModel):
  jsonFields = ["path", "mapFilters"]
  date = models.DateTimeField('Date de Reception', blank=True, null=True, default=None)
  user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
  view = models.BooleanField('Geo ou Enseigne', unique=False, blank=False, default=False)
  year = models.BooleanField('Année selectionnée', unique=False, blank=False, default=False)
  path = models.CharField("Navigation", max_length=64, unique=False, blank=False, default=None)
  dashboard = models.ForeignKey(Dashboard, on_delete=models.DO_NOTHING, null=True, default=None)
  pdv = models.ForeignKey(Pdv, on_delete=models.DO_NOTHING, null=True, default=None)
  mapVisible = models.BooleanField('Tableau de bord ou cartographie', unique=False, blank=False, default=False)
  mapFilters = models.CharField("CategorieSelectionnée", max_length=1024, unique=False, blank=False, default=None)
  widgetParams = models.ForeignKey(WidgetParams, on_delete=models.DO_NOTHING, null=True, default=None)
  stayConnected = models.BooleanField('Resté connecté', unique=False, blank=False, default=False)
  

  @classmethod
  def createFromList(cls, data, user, now):
    kwargs, data = {}, [False, False] + data
    listFields = cls.listFields()
    for index in range(len(listFields)):
      field = listFields[index]
      if field == "date":
        kwargs[field] = now
      elif field == "user":
        kwargs[field] = user.user
      elif field in cls.jsonFields:
        kwargs[field] = json.dumps(data[index])
      elif isinstance(cls._meta.get_field(field), models.ForeignKey):
        objectField = Dashboard.objects.get(id=data[index]) if data[index] else None
        kwargs[field] = objectField
      elif isinstance(cls._meta.get_field(field), models.BooleanField):
        kwargs[field] = True if data[index] else False
      else:
        kwargs[field] = data[index]
    cls.objects.create(**kwargs)



