from django.db import models
from django.contrib.auth.models import User
from datetime import date
import json
from django.db.models.fields import Field

from django.forms.models import model_to_dict

class CommonModel(models.Model):
  """jsonFields tells which field are to be loaded, and direct fields tells which fields should contain the dict of the sub object."""
  jsonFields = []
  direct = {}
  currentYear = True

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
    if getattr(cls, "currentField", False):
      return {instance.id:instance.listValues for instance in cls.objects.filter(currentYear=True)}
    return {instance.id:instance.listValues for instance in cls.objects.all()}

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

  @property
  def listValues(self):
    listFields = self.listFields()
    listRow = [getattr(self, field, False) for field in listFields]
    for index in self.listIndexes():
      if isinstance(self._meta.get_field(listFields[index]), models.ManyToManyField):
        listRow[index] = [element.id for element in listRow[index].all()]
    if self.jsonFields:
      for jsonField in self.jsonFields:
        index = self.listFields().index(jsonField)
        listRow[index] = json.loads(listRow[index])
    self.__loadDirectValue(listRow)
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

class Drv(models.Model):
  name = models.CharField('drv', max_length=16, unique=False)
  currentYear = models.BooleanField("Année courante", default=True)

  class Meta:
    verbose_name = "DRV"

  def __str__(self) ->str:
    return self.name

class Agent(models.Model):
  name = models.CharField('agent', max_length=64, unique=False)
  drv = models.ForeignKey('drv', on_delete=models.PROTECT, blank=False)
  currentYear = models.BooleanField("Année courante", default=True)

  class Meta:
    verbose_name = "Secteur"

  def __str__(self) ->str:
    return self.name

class AgentFinitions(models.Model):
  name = models.CharField('agent_finitions', max_length=64, unique=False)
  drv = models.ForeignKey('drv', on_delete=models.PROTECT, blank=False)
  currentYear = models.BooleanField("Année courante", default=True)

  class Meta:
    verbose_name = "Agent Finitions"

  def __str__(self) ->str:
    return self.name

class Dep(models.Model):
  name = models.CharField('dep', max_length=2, unique=False)
  currentYear = models.BooleanField("Année courante", default=True)

  class Meta:
    verbose_name = "Département"

  def __str__(self) ->str:
    return self.name

class Bassin(models.Model):
  name = models.CharField('bassin', max_length=64, unique=False)
  currentYear = models.BooleanField("Année courante", default=True)

  class Meta:
    verbose_name = "Bassin"

  def __str__(self) ->str:
    return self.name

class Ville(models.Model):
  name = models.CharField('ville', max_length=128, unique=True)

  class Meta:
    verbose_name = "Ville"

  def __str__(self) ->str:
    return self.name

class SegmentMarketing(models.Model):
  name = models.CharField('segment_marketing', max_length=32, unique=False)
  currentYear = models.BooleanField("Année courante", default=True)

  class Meta:
    verbose_name = "Segment Marketing"

  def __str__(self) ->str:
    return self.name

class SegmentCommercial(models.Model):
  name = models.CharField('segment_commercial', max_length=16, unique=False)
  currentYear = models.BooleanField("Année courante", default=True)

  class Meta:
    verbose_name = "Segment Commercial"

  def __str__(self) ->str:
    return self.name

class Enseigne(models.Model):
  name = models.CharField('name', max_length=64, unique=False, blank=False, default="Inconnu")
  currentYear = models.BooleanField("Année courante", default=True)

  class Meta:
    verbose_name = "Enseigne"

  def __str__(self) ->str:
    return self.name

class Ensemble(models.Model):
  name = models.CharField('name', max_length=64, unique=False, blank=False, default="Inconnu")
  enseigne = models.ForeignKey('enseigne', on_delete=models.PROTECT, blank=False, default=7)
  currentYear = models.BooleanField("Année courante", default=True)

  class Meta:
    verbose_name = "Ensemble"

  def __str__(self) ->str:
    return self.name

class SousEnsemble(models.Model):
  name = models.CharField('name', max_length=64, unique=False, blank=False, default="Inconnu")
  currentYear = models.BooleanField("Année courante", default=True)

  class Meta:
    verbose_name = "Sous-Ensemble"

  def __str__(self) ->str:
    return self.name

class Site(models.Model):
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

  @property
  def listValues(self):
    lv = super().listValues
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
    raw[0] = raw[0].isoformat()
    return raw


# Modèles pour l'AD

class Produit(models.Model):
  name = models.CharField('name', max_length=32, unique=True, blank=False, default="Inconnu")

  class Meta:
    verbose_name = "Produit"

  def __str__(self) ->str:
    return self.name

class Industrie(models.Model):
  name = models.CharField('name', max_length=32, unique=True, blank=False, default="Inconnu")

  class Meta:
    verbose_name = "Industrie"

  def __str__(self) ->str:
    return self.name

class Ventes(models.Model):
  date = models.DateTimeField('Date de Saisie', blank=True, null=True, default=None)
  pdv = models.ForeignKey("PDV", on_delete=models.CASCADE, blank=False, default=1)
  industry = models.ForeignKey("Industrie", on_delete=models.PROTECT, blank=False, default=17)
  product = models.ForeignKey("Produit", on_delete=models.CASCADE, blank=False, default=6)
  volume = models.FloatField('Volume', unique=False, blank=True, default=0.0)
  currentYear = models.BooleanField("Année courante", default=True)

  class Meta:
    verbose_name = "Ventes"
    unique_together = ('pdv', 'industry', 'product')

  def __str__(self) ->str:
    return str(self.pdv) + " " + str(self.industry) + " " + str(self.product)


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
  
class WidgetParams(models.Model):
  title = models.CharField(max_length=32, unique=False, blank=False, default=None)
  subTitle = models.CharField(max_length=2048, unique=False, blank=False, default=None)
  position = models.CharField(max_length=1, unique=False, blank=False, default=None)
  unity = models.CharField("Unité", max_length=32, unique=False, blank=False, default=None)
  widget = models.ForeignKey('Widget', on_delete=models.DO_NOTHING, blank=False, null=False, default=None)
  widgetCompute = models.ForeignKey("WidgetCompute", on_delete=models.DO_NOTHING, blank=False, default=None)

  @classmethod
  def listFields(cls): return ["title", "subTitle", "unity", "widget", "widgetCompute"]

  @property
  def listValues(self):
    listOld = super().listValues


class WidgetCompute(CommonModel):
  jsonFields = ["groupAxis1", "groupAxis2"]
  axis1 = models.CharField("Axe 1", max_length=32, unique=False, blank=False, default=None)
  axis2 = models.CharField("Axe 2", max_length=32, unique=False, blank=False, default=None)
  indicator = models.CharField("Indicateur", max_length=32, unique=False, blank=False, default=None)
  groupAxis1 = models.CharField("Filtre Axe 1", max_length=4096, unique=False, blank=False, default=None)
  groupAxis2 = models.CharField("Filtre Axe 2", max_length=4096, unique=False, blank=False, default=None)
  percent = models.CharField("Pourcentage", max_length=32, unique=False, blank=False, default="no")


class Dashboard(CommonModel):
  name = models.CharField(max_length=64, unique=False, blank=False, default=None)
  layout = models.ForeignKey('Layout', on_delete=models.PROTECT, blank=False, default=1)
  comment = models.CharField(max_length=2048, unique=False, blank=False, default=None)
  widgetParams = models.ManyToManyField("WidgetParams")

  @classmethod
  def listFields(csl): return ["name", "layout", "comment", "widgetParams"]

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

class Ciblage(models.Model):
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

class CiblageLevel(models.Model):
  date = models.DateTimeField('Date de Saisie', blank=True, null=True, default=None)
  agent = models.ForeignKey('Agent', on_delete=models.DO_NOTHING, blank=True, null=True, default=None)
  drv = models.ForeignKey('Drv', on_delete=models.DO_NOTHING, blank=True, null=True, default=None)
  volP2CD = models.FloatField('Cible visée en Volume P2CD', unique=False, blank=False, default=0.0)
  dnP2CD = models.IntegerField('Cible visée en dn P2CD', unique=False, blank=False, default=0)
  volFinition= models.FloatField('Cible visée en Volume Enduit', unique=False, blank=False, default=0.0)
  dnFinition = models.IntegerField('Cible visée en dn Enduit', unique=False, blank=False, default=0)



