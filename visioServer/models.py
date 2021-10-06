from django.db import models
from django.contrib.auth.models import User
from datetime import date
import json
# from django.db.models.fields import Field
import datetime
import inspect

# from django.forms.models import model_to_dict

class CommonModel(models.Model):
  """jsonFields tells which field are to be loaded, and direct fields tells which fields should contain the dict of the sub object."""
  jsonFields = []
  direct = {}

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
  def dictValues(cls):
    length = len(cls.listFields()) == 1
    if getattr(cls, "currentYear", False):
      result = {instance.id:instance.listValues[0] if length else instance.listValues for instance in cls.objects.filter(currentYear=True)}
      return result
    return {instance.id:instance.listValues[0] if length else instance.listValues for instance in cls.objects.all()}

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

  @property
  def listValues(self):
    listFields = self.listFields()
    listRow = [getattr(self, field, False) for field in listFields]
    if "date" in listFields:
      indexDate = listFields.index("date")
      listRow[indexDate] = listRow[indexDate].isoformat() if listRow[indexDate] else None
    for index in self.listIndexes():
      if isinstance(self._meta.get_field(listFields[index]), models.ManyToManyField):
        listRow[index] = [element.id for element in listRow[index].all()]
      else:
        listRow[index] = listRow[index].id
    if self.jsonFields:
      for jsonField in self.jsonFields:
        index = self.listFields().index(jsonField)
        listRow[index] = json.loads(listRow[index])
    # self.__loadDirectValue(listRow)
    return listRow

  def __loadDirectValue(self, listRow):
    if self.direct:
      for key in self.direct.keys():
        if key == "father":
          index = self.listFields().index(key)
          listRow[index] = []
          children = self.__class__.objects.filter(father=self)
          for child in children:
            listRow[index].append(child.listValues)

# Information Params
class ParamVisio(CommonModel):
  field = models.CharField(max_length=64, unique=True, blank=False)
  prettyPrint = models.CharField(max_length=64, unique=False, blank=False, default=None)
  fvalue = models.CharField(max_length=64, unique=False, blank=False)
  typeValue = models.CharField(max_length=64, unique=False, blank=False)

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
    return self.fvalue

class Drv(CommonModel):
  name = models.CharField('drv', max_length=16, unique=False)
  currentYear = models.BooleanField("Année courante", default=True)

  class Meta:
    verbose_name = "DRV"

  def __str__(self) ->str:
    return self.name

class Agent(CommonModel):
  name = models.CharField('agent', max_length=64, unique=False)
  currentYear = models.BooleanField("Année courante", default=True)

  class Meta:
    verbose_name = "Secteur"

  def __str__(self) ->str:
    return self.name

class AgentFinitions(CommonModel):
  name = models.CharField('agent_finitions', max_length=64, unique=False)
  currentYear = models.BooleanField("Année courante", default=True)

  class Meta:
    verbose_name = "Agent Finitions"

  def __str__(self) ->str:
    return self.name

class Dep(CommonModel):
  name = models.CharField('dep', max_length=2, unique=False)
  currentYear = models.BooleanField("Année courante", default=True)

  class Meta:
    verbose_name = "Département"

  def __str__(self) ->str:
    return self.name

class Bassin(CommonModel):
  name = models.CharField('bassin', max_length=64, unique=False)
  currentYear = models.BooleanField("Année courante", default=True)

  class Meta:
    verbose_name = "Bassin"

  def __str__(self) ->str:
    return self.name

  @property
  def listValues(self):
    return [bassin.replace("Négoce_", "") for bassin in super().listValues]

class Ville(CommonModel):
  name = models.CharField('ville', max_length=128, unique=True)

  class Meta:
    verbose_name = "Ville"

  def __str__(self) ->str:
    return self.name

class SegmentMarketing(CommonModel):
  name = models.CharField('segment_marketing', max_length=32, unique=False)
  currentYear = models.BooleanField("Année courante", default=True)

  class Meta:
    verbose_name = "Segment Marketing"

  def __str__(self) ->str:
    return self.name

class SegmentCommercial(CommonModel):
  name = models.CharField('segment_commercial', max_length=16, unique=False)
  currentYear = models.BooleanField("Année courante", default=True)

  class Meta:
    verbose_name = "Segment Commercial"

  def __str__(self) ->str:
    return self.name

class Enseigne(CommonModel):
  name = models.CharField('name', max_length=64, unique=False, blank=False, default="Inconnu")
  currentYear = models.BooleanField("Année courante", default=True)

  class Meta:
    verbose_name = "Enseigne"

  def __str__(self) ->str:
    return self.name

class Ensemble(CommonModel):
  name = models.CharField('name', max_length=64, unique=False, blank=False, default="Inconnu")
  currentYear = models.BooleanField("Année courante", default=True)

  class Meta:
    verbose_name = "Ensemble"

  def __str__(self) ->str:
    return self.name

class SousEnsemble(CommonModel):
  name = models.CharField('name', max_length=64, unique=False, blank=False, default="Inconnu")
  currentYear = models.BooleanField("Année courante", default=True)

  class Meta:
    verbose_name = "Sous-Ensemble"

  def __str__(self) ->str:
    return self.name

class Site(CommonModel):
  name = models.CharField('name', max_length=64, unique=False, blank=False, default="Inconnu")
  currentYear = models.BooleanField("Année courante", default=True)

  class Meta:
    verbose_name = "Site"

  def __str__(self) ->str:
    return self.name

class Pdv(CommonModel):
  code = models.CharField('PDV code', max_length=10, blank=False, default="Inconnu")
  name = models.CharField('PDV', max_length=64, blank=False, default="Inconnu")
  drv = models.ForeignKey('drv', verbose_name='Région', on_delete=models.PROTECT,  blank=False)
  agent = models.ForeignKey('agent', verbose_name='Secteur', on_delete=models.PROTECT, blank=False)
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
  redistributedEnduit = models.BooleanField("redistribué Enduit", default=True)
  pointFeu = models.BooleanField('Point Feu', default=False)
  closedAt = models.DateTimeField('Date de Fermeture', blank=True, null=True, default=None)
  currentYear = models.BooleanField("Année courante", default=True)

  def __str__(self) ->str: return self.name + " " + self.code

  @classmethod
  def listFields(cls):
    return super().listFields() + ["nbVisits", "target", "sales"]

  @classmethod
  def dictValues(cls):
    indexSale = cls.listFields().index("sale")
    return {id:value for id, value in super().dictValues().items() if value[indexSale]}

  @property
  def listValues(self):
    lv = super().listValues
    if isinstance(lv[20], datetime.datetime):
      lv[20] = lv[20].isoformat()
    lv[21] = sum([visit.nbVisitCurrentYear for visit in Visit.objects.filter(pdv=self)])
    target = Ciblage.objects.filter(pdv = self)
    if target:
      lv[22] = target[0].listValues
    lv[23] = [vente.listValues for vente in Ventes.objects.filter(pdv=self)]
    return lv

class Visit(CommonModel):
  date = models.DateField(verbose_name="Mois des visites", default=date.today)
  nbVisit = models.IntegerField(verbose_name="Nombre de visites", blank=False, default=1)
  pdv = models.ForeignKey("PDV", on_delete=models.CASCADE, blank=False, null=False, default=1)
  currentYear = None
  try:
    currentYear = ParamVisio.objects.filter(field="currentYear")
    currentYear = currentYear[0].value if currentYear else None
  except:
    pass

  class Meta:
    verbose_name = "Visites Mensuels"

  @property
  def nbVisitCurrentYear(self):
    if self.date.year == self.currentYear:
      return self.nbVisit
    return 0

  def __str__(self) ->str:
    return self.date.strftime("%Y-%m") + " " + self.pdv.code

  @property
  def listValues(self):
    raw = super().listValues
    del raw[2]
    return raw


# Modèles pour l'AD

class Produit(CommonModel):
  name = models.CharField('name', max_length=32, unique=True, blank=False, default="Inconnu")

  class Meta:
    verbose_name = "Produit"

  def __str__(self) ->str:
    return self.name

class Industrie(CommonModel):
  name = models.CharField('name', max_length=32, unique=True, blank=False, default="Inconnu")

  class Meta:
    verbose_name = "Industrie"

  def __str__(self) ->str:
    return self.name

class Ventes(CommonModel):
  date = models.DateTimeField('Date de Saisie', blank=True, null=True, default=None)
  pdv = models.ForeignKey("PDV", on_delete=models.CASCADE, blank=False, default=1)
  industry = models.ForeignKey("Industrie", on_delete=models.PROTECT, blank=False, default=17)
  product = models.ForeignKey("Produit", on_delete=models.CASCADE, blank=False, default=6)
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

  @classmethod
  def createCache(cls):
    sales = Ventes.objects.all()
    salesDict = {}
    for sale in sales:
      id = str(sale.pdv.id)
      if id not in salesDict:
          salesDict[id] = []
      salesDict[id].append(sale.listValues)
    return salesDict

  @classmethod
  def createSalesDict(cls):
    if cls.isNotOnServer and not cls.salesDict:
      try:
        with open(cls.cacheSalesDict, 'r') as jsonFile:
          cls.salesDict = json.load(jsonFile)
      except:
        print('Formating sales...')
      
      if not cls.salesDict:
        cls.salesDict = cls.createCache()
        if cls.isNotOnServer:
          with open(cls.cacheSalesDict, 'w') as jsonFile:
            json.dump(cls.salesDict, jsonFile)



# Modèles pour la navigation
class TreeNavigation(CommonModel):
  direct = {"father":"children"}
  geoOrTrade = models.CharField(max_length=6, unique=False, blank=False, default="Geo")
  level = models.CharField(max_length=32, unique=True, blank=False, default=None)
  name = models.CharField(max_length=32, unique=False, blank=False, default=None)
  father = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)

class Layout(CommonModel):
  jsonFields = ["template"]
  name = models.CharField(max_length=64, unique=True, blank=False, default=None)
  template = models.CharField(max_length=2048, unique=False, blank=False, default=None)

class Widget(CommonModel):
  name = models.CharField(max_length=32, unique=True, blank=False, default=None)
  
class WidgetParams(CommonModel):
  jsonFields = ["subTitle"]
  title = models.CharField(max_length=32, unique=False, blank=False, default=None)
  subTitle = models.CharField(max_length=2048, unique=False, blank=False, default=None)
  position = models.CharField(max_length=1, unique=False, blank=False, default=None)
  unity = models.CharField("Unité", max_length=32, unique=False, blank=False, default=None)
  widget = models.ForeignKey('Widget', on_delete=models.DO_NOTHING, blank=False, null=False, default=None)
  widgetCompute = models.ForeignKey("WidgetCompute", on_delete=models.DO_NOTHING, blank=False, default=None)

  @classmethod
  def listFields(cls): return ["title", "subTitle", "unity", "widget", "widgetCompute"]


class WidgetCompute(CommonModel):
  jsonFields = ["groupAxis1", "groupAxis2"]
  axis1 = models.CharField("Axe 1", max_length=32, unique=False, blank=False, default=None)
  axis2 = models.CharField("Axe 2", max_length=32, unique=False, blank=False, default=None)
  indicator = models.CharField("Indicateur", max_length=32, unique=False, blank=False, default=None)
  groupAxis1 = models.CharField("Filtre Axe 1", max_length=4096, unique=False, blank=False, default=None)
  groupAxis2 = models.CharField("Filtre Axe 2", max_length=4096, unique=False, blank=False, default=None)
  percent = models.CharField("Pourcentage", max_length=32, unique=False, blank=False, default="no")


class Dashboard(CommonModel):
  jsonFields = ["comment"]
  name = models.CharField(max_length=64, unique=False, blank=False, default=None)
  layout = models.ForeignKey('Layout', on_delete=models.PROTECT, blank=False, default=1)
  comment = models.CharField(max_length=2048, unique=False, blank=False, default=None)
  widgetParams = models.ManyToManyField("WidgetParams")

  @classmethod
  def listFields(csl): return ["name", "layout", "comment", "widgetParams"]

  @property
  def listValues(self):
      lv = super().listValues
      listObjWidgetParam = [WidgetParams.objects.get(id = wp.id) for wp in self.widgetParams.all()]
      indexWP = self.listFields().index("widgetParams")
      lv[indexWP] = {object.position:object.id for object in listObjWidgetParam}
      return lv


class DashboardTree(models.Model):
  geoOrTrade = models.CharField(max_length=6, unique=False, blank=False, default="Geo")
  profile = models.CharField(max_length=32, blank=False, default=None)
  level = models.ForeignKey("TreeNavigation", on_delete=models.PROTECT, blank=False, default=None)
  dashboards = models.ManyToManyField("Dashboard")

class LabelForGraph(CommonModel):
  axisType = models.CharField(max_length=32, unique=False, blank=False, default=None)
  label = models.CharField(max_length=32, unique=False, blank=False, default=None)
  color = models.CharField(max_length=32, unique=False, blank=False, default=None)

  def __str__(self) ->str:
    return "LabelForGraph " + str(self.axisType) + " " + str(self.label) + " " + str(self.color)

class AxisForGraph(CommonModel):
  name = models.CharField(max_length=32, unique=False, blank=False, default=None)
  labels = models.ManyToManyField("LabelForGraph")

  class Meta:
    verbose_name = "Axes pour les graphiques"

  @classmethod
  def listFields(cls): return ["name", "labels"]

  # @classmethod
  # def listFields(cls): return ["name", "labels"]
  
  def __str__(self) ->str:
    return "AxisForGraph " + str(self.name)


# Informations complémentaire pour les users profile

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    idGeo = models.IntegerField(blank=True, default=None)

# Information ciblage

class Ciblage(CommonModel):
  date = models.DateTimeField('Date de Saisie', blank=True, null=True, default=None)
  pdv = models.ForeignKey("PDV", on_delete=models.CASCADE, blank=False, default=1)
  redistributed = models.BooleanField("Redistribué", default=True)
  sale = models.BooleanField("Ne vend pas de plaque", default=True)
  targetP2CD = models.FloatField('Cible P2CD', unique=False, blank=True, default=0.0)
  targetFinition = models.BooleanField('Cible Finitions', unique=False, blank=False, default=False)
  GREEN = 'g'
  ORANGE = 'o'
  RED = 'r'
  COLORS_GREEN_LIGHT_CHOICES = [(GREEN, 'vert'), (ORANGE,'orange'), (RED, 'rouge')] 
  greenLight = models.CharField("Feu Ciblage P2CD", max_length=1, choices=COLORS_GREEN_LIGHT_CHOICES, blank=True, default=None)
  commentTargetP2CD = models.TextField("Commentaires ciblage P2CD", blank=True, default=None)
  targetsDict = None

  @classmethod
  def listFields(cls):
    lf = super().listFields()
    del lf[1]
    return lf

  @classmethod
  def createCache(cls):
    cls.targetsDict = {target.pdv.id:target.listValues for target in cls.objects.all()}

  @classmethod
  def createTargetDict(cls):
    fileName = Ventes.cacheSalesDict.replace("sales", "targets")
    if Ventes.isNotOnServer and not cls.targetsDict:
      try:
        with open(fileName, 'r') as jsonFile:
          cls.targetsDict = json.load(jsonFile)
      except:
        print('Formating targets...')
      
      if not cls.targetsDict:
        cls.createCache()
        if Ventes.isNotOnServer:
          with open(fileName, 'w') as jsonFile:
            json.dump(cls.targetsDict, jsonFile)


class CiblageLevel(models.Model):
  date = models.DateTimeField('Date de Saisie', blank=True, null=True, default=None)
  agent = models.ForeignKey('Agent', on_delete=models.DO_NOTHING, blank=True, null=True, default=None)
  drv = models.ForeignKey('Drv', on_delete=models.DO_NOTHING, blank=True, null=True, default=None)
  volP2CD = models.FloatField('Cible visée en Volume P2CD', unique=False, blank=False, default=0.0)
  dnP2CD = models.IntegerField('Cible visée en dn P2CD', unique=False, blank=False, default=0)
  volFinition= models.FloatField('Cible visée en Volume Enduit', unique=False, blank=False, default=0.0)
  dnFinition = models.IntegerField('Cible visée en dn Enduit', unique=False, blank=False, default=0)



