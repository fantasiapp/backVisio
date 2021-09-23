from visioServer.models import WidgetCompute, WidgetParams, Widget, Layout
import json

class CreateWidgetParam:
  __dictWidget = {}
  dictLayout = None
  dashboards = {
      "geo":{"Marché P2CD":"column:2:1", "Marché Enduit":"column:2:1", "PdM P2CD":"column:2:1", "PdM Enduit":"column:2:1",
      "PdM P2CD Simulation":"column:2:1", "PdM Enduit Simulation":"column:2:1", "DN P2CD":"column:2:1", "DN Enduit":"column:2:1",
      "DN P2CD Simulation":"column:2:1", "DN Enduit Simulation":"column:2:1", "Points de Vente P2CD":"mono",
      "Points de Vente Enduit":"mono", "Synthèse P2CD":"row:1:1:1", "Synthèse Enduit":"row:1:1:1",
      "Synthèse P2CD Simulation":"column:2:1", "Synthèse Enduit Simulation":"column:2:1", "Suivi AD":"row:2:1",
      "Suivi des Visites":"row:2:2"},
      "trade":{"Marché P2CD Enseigne":"column:2:1", "Marché Enduit Enseigne":"column:2:1",
      "PdM P2CD Enseigne":"column:2:1", "PdM Enduit Enseigne":"column:2:1"}
    }
  dashboardsLevel = {"geo":{"root":["Marché P2CD", "Marché Enduit", "PdM P2CD", "PdM Enduit", "PdM P2CD Simulation", "PdM Enduit Simulation", "DN P2CD", "DN Enduit",
    "DN P2CD Simulation", "DN Enduit Simulation", "Points de Vente P2CD", "Points de Vente Enduit", "Synthèse P2CD", "Synthèse Enduit",
    "Synthèse P2CD Simulation", "Synthèse Enduit Simulation", "Suivi AD", "Suivi des Visites"],

    "drv":["Marché P2CD", "Marché Enduit", "PdM P2CD", "PdM Enduit", "PdM P2CD Simulation", "PdM Enduit Simulation", "DN P2CD", "DN Enduit",
    "DN P2CD Simulation", "DN Enduit Simulation", "Points de Vente P2CD", "Points de Vente Enduit", "Synthèse P2CD", "Suivi des Visites"],

    "agent":["Marché P2CD", "Marché Enduit", "PdM P2CD", "PdM Enduit", "PdM P2CD Simulation", "DN P2CD", "DN Enduit",
    "DN P2CD Simulation", "Points de Vente P2CD", "Points de Vente Enduit"],

    "dep":["Marché P2CD", "Marché Enduit", "PdM P2CD", "PdM Enduit", "PdM P2CD Simulation", "DN P2CD", "DN Enduit",
    "DN P2CD Simulation", "Points de Vente P2CD", "Points de Vente Enduit"],

    "bassin":["Marché P2CD", "Marché Enduit", "PdM P2CD", "PdM Enduit", "PdM P2CD Simulation", "DN P2CD", "DN Enduit",
    "DN P2CD Simulation", "Points de Vente P2CD", "Points de Vente Enduit"]
    },
    "trade":{
      "rootTrade":["Marché P2CD Enseigne", "Marché Enduit Enseigne", "PdM P2CD Enseigne", "PdM Enduit Enseigne", "DN P2CD", "DN Enduit",
      "Points de Vente P2CD", "Points de Vente Enduit", "Synthèse P2CD", "Synthèse Enduit"],

      "enseigne":["Marché P2CD Enseigne", "Marché Enduit Enseigne", "PdM P2CD Enseigne", "PdM Enduit Enseigne", "DN P2CD", "DN Enduit",
      "Points de Vente P2CD", "Points de Vente Enduit", "Synthèse P2CD", "Synthèse Enduit"],

      "ensemble":["Marché P2CD Enseigne", "Marché Enduit Enseigne", "PdM P2CD Enseigne", "PdM Enduit Enseigne", "DN P2CD", "DN Enduit",
      "Points de Vente P2CD", "Points de Vente Enduit", "Synthèse P2CD", "Synthèse Enduit"],

      "sousEnsemble":["Marché P2CD Enseigne", "Marché Enduit Enseigne", "PdM P2CD Enseigne", "PdM Enduit Enseigne", "DN P2CD", "DN Enduit",
      "Points de Vente P2CD", "Points de Vente Enduit", "Synthèse P2CD", "Synthèse Enduit"]}
    }
  

  @classmethod
  def initialize(cls):
    if not cls.__dictWidget:
      for name in ["pie", "donut", "image", "histoRow", "histoColumn", "table", "pieTarget"]:
        cls.__dictWidget[name] = Widget.objects.create(name=name)
    if not cls.dictLayout:
      cls.dictLayout = {}
      data = {
        "column:2:1":[["a","c"],["b","c"]],
        "mono":[["a"]],
        "row:1:1:1":[["a"],["b"],["c"]],
        "row:1I:1:1I":[["a"],["b"],["c"]],
        "row:2:1":[["a", "b"], ["c", "c"]],
        "row:2:2":[["a","b"], ["c", "d"]]
      }
      for name, jsonLayout in data.items():
        object = Layout.objects.create(name=name, template=json.dumps(jsonLayout))
        cls.dictLayout[name] = object


  @classmethod
  def create(cls, name):
    dictParam = {
      "Marché P2CD":[
        ["segmentMarketing", "segmentCommercial", "p2cd", [], ["@other"], "no", "Vente en volume", "@sum"],
        ["segmentMarketing", "segmentCommercial", "dn", [], ["@other"], "no", "Nombre de Pdv", "@sum", "b", "Pdv", "donut"],
        ["enseigne", "industrie", "p2cd", [], ["Siniat", "Placo", "Knauf", "Challengers"], "no", "Volume par enseigne", "", "c", "km²", "histoRow"]
      ], "Marché Enduit":[
        ["enduitIndustrie", "segmentCommercial", "enduit", [], ["@other"], "no", "Volume Total", "@sum", "a", "T"],
        ["segmentDnEnduit", "segmentCommercial", "dn", [], ["@other"], "no", "Nombre de Pdv", "@sum", "b", "Pdv", "donut"],
        ["enseigne", "enduitIndustrie", "enduit", [], [], "no", "Volume par enseigne", "Tous segments", "c", "T", "histoRow"]
      ], "PdM P2CD":[
        ["industrie", "segmentMarketing", "p2cd", ["Siniat", "Placo", "Knauf", "Challengers"], ["@other"], "classic", "Pdm Total", "", "a", "%"],
        ["industrie", "segmentMarketing", "p2cd", ["Siniat", "Placo", "Knauf", "Challengers"], [], "cols", "Par segment", "", "b", "%", "histoColumn"],
        ["enseigne", "industrie", "p2cd", [], ["Siniat", "Placo", "Knauf", "Challengers"], "classic", "Par Enseigne", "Tous segments", "c", "%", "histoRow"]
      ], "PdM Enduit":[
        ["enduitIndustrie", "segmentCommercial", "Enduit", [], ["@other"], "classic", "Pdm Total", "", "a", "%"],
        ["enduitIndustrie", "segmentMarketing", "Enduit", [], [], "cols", "Par segment", "", "b", "%", "histoColumn"],
        ["enseigne", "enduitIndustrie", "Enduit", [], [], "classic", "Par Enseigne", "", "c", "%", "histoRow"]
      ], "PdM P2CD Simulation":[
        ["industrieTarget", "segmentMarketing", "p2cd", ["Siniat", "Potentiel", "Placo", "Knauf", "Challengers"], ["@other"], "classic", "Par Industrie", "", "a", "%", "pieTarget"],
        ["industrieTarget", "segmentMarketing", "p2cd", ["Siniat", "Potentiel", "Placo", "Knauf", "Challengers"], [], "cols", "Par segment", "", "b", "%", "histoColumn"],
        ["enseigne", "industrieTarget", "p2cd", [], ["Siniat", "Potentiel", "Placo", "Knauf", "Challengers"], "classic", "Par Enseigne", "Tous segments", "c", "%", "histoRow"]
      ], "PdM Enduit Simulation":[
        ["enduitIndustrieTarget", "segmentCommercial", "Enduit", [], ["@other"], "classic", "Pdm Total", "", "a", "%", "pieTarget"],
        ["enduitIndustrieTarget", "segmentMarketing", "Enduit", [], [], "cols", "Par segment", "", "b", "%", "histoColumn"],
        ["enseigne", "enduitIndustrieTarget", "Enduit", [], [], "classic", "Par Enseigne", "", "c", "%", "histoRow"]
      ], "DN P2CD":[
        ["clientProspect", "segmentMarketing", "dn", [], ["@other"], "no", "Par Segment", "Nombre de Pdv Client/Prospect", "a", "Pdv", "donut"],
        ["clientProspect", "segmentMarketing", "dn", [], [], "no", "Par Client et Prospect", "", "b", "Pdv", "histoColumn"],
        ["enseigne", "clientProspect", "dn", [], [], "no", "Par Enseigne", "Tous Segments", "c", "Pdv", "histoRow"]
      ], "DN Enduit":[
        ["segmentDnEnduit", "segmentCommercial", "dn", [], ["@other"], "no", "DN totale", "", "a", "Pdv", "donut"],
        ["segmentDnEnduit", "segmentMarketing", "dn", [], [], "no", "Par segment", "", "b", "Pdv", "histoColumn"],
        ["enseigne", "segmentDnEnduit", "dn", [], [], "no", "Par Enseigne", "Tous Segments", "c", "Pdv", "histoRow"]
      ], "DN P2CD Simulation":[
        ["clientProspectTarget", "segmentCommercial", "dn", [], ["@other"], "no", "Par Client et Prospect", "", "a", "Pdv", "pieTarget"],
        ["clientProspectTarget", "segmentMarketing", "dn", [], [], "no", "Par Segment", "", "b", "Pdv", "histoColumn"],
        ["enseigne", "clientProspectTarget", "dn", [], [], "no", "Par Enseigne", "Tous Segments", "c", "Pdv", "histoRow"]
      ], "DN Enduit Simulation":[
        ["segmentDnEnduitTarget", "segmentCommercial", "dn", [], ["@other"], "no", "DN totale", "", "a", "Pdv", "donut"],
        ["segmentDnEnduitTarget", "segmentMarketing", "dn", [], [], "no", "Par segment", "", "b", "Pdv", "histoColumn"],
        ["enseigne", "segmentDnEnduitTarget", "dn", [], [], "no", "Par Enseigne", "Tous Segments", "c", "Pdv", "histoRow"]
      ], "Points de Vente P2CD":[
        ["pdvs", "colTableP2cd", "p2cd", [], [], "no", "@titleTableP2cd", "", "a", "m²", "table"]
      ], "Points de Vente Enduit":[
        ["pdvs", "colTableEnduit", "enduit", [], [], "no", "@titleTableEnduit", "", "a", "T", "table"]
      ], "Synthèse P2CD":[
        ["industrie", "lg-1", "P2CD", ["Siniat", "Concurrence"], [], "no", "", "", "a", "km²", "histoColumn"],
        ["industrie", "lg-1", "P2CD", ["Siniat", "Placo", "Knauf", "Challengers"], [], "cols", "", "", "b", "%", "histoColumn"],
        ["clientProspect", "lg-1", "dn", [], [], "no", "", "", "c", "Pdv", "histoColumn"]
      ], "Synthèse Enduit":[
        ["enduitIndustrie", "lg-1", "enduit", [], [], "no", "", "", "a", "T", "histoColumn"],
        ["enduitIndustrie", "lg-1", "enduit", [], [], "cols", "", "", "b", "%", "histoColumn"],
        ["segmentDnEnduit", "lg-1", "dn", [], [], "no", "", "", "c", "Pdv", "histoColumn"]
      ], "Synthèse P2CD Simulation":[
        ["industrie", "segmentMarketing", "P2CD", ["Siniat", "Placo", "Knauf", "Challengers"], [], "no", "Volume par segment", "", "a", "histoColumn"],
        ["industrie", "segmentMarketing", "P2CD", ["Siniat", "Placo", "Knauf", "Challengers"], [], "classic", "Volume par segment", "", "b", "histoColumn"],
        ["enseigne", "segmentMarketing", "dn", ["Siniat", "Placo", "Knauf", "Challengers"], [], "no", "Tous Segment", "", "c", "histoColumn"]
      ], 'Suivi des Visites':[
        ["segmentMarketing", "segmentCommercial", "p2cd", [], ["@other"], "no", "Vente en volume"],
        ["segmentMarketing", "segmentCommercial", "dn", [], ["@other"], "no", "Nombre de Pdv", "", "b"],
        ["segmentMarketing", "segmentCommercial", "p2cd", [], ["@other"], "no", "Vente en volume", "", "c"],
        ["segmentMarketing", "segmentCommercial", "dn", [], ["@other"], "no", "Nombre de Pdv", "", "d"],
      ], 'other':[
        ["segmentMarketing", "segmentCommercial", "p2cd", [], ["@other"], "no", "Vente en volume"],
        ["segmentMarketing", "segmentCommercial", "dn", [], ["@other"], "no", "Nombre de Pdv", "", "b"],
        ["enseigne", "industrie", "p2cd", [], ["Siniat", "Placo", "Knauf", "Challengers"], "no", "Volume par enseigne", "", "c", "histoRow"],
        ["enseigne", "industrie", "dn", [], ["Siniat", "Placo", "Knauf", "Challengers"], "no", "Volume par industrie", "", "c", "histoColumn"]
      ]
    }
    params = dictParam[name] if name in dictParam else dictParam['other']
    paramName = ["axis1", "axis2", "ind", "grAx1", "grAx2", "percent", "title", "subTitle", "pos", "unity", "widget"]
    return [cls.executeCreation(**{paramName[i]:param[i] for i in range(len(param))}) for param in params]

  @classmethod
  def executeCreation(cls, axis1, axis2, ind, grAx1, grAx2, percent=False, title="Titre", subTitle="", pos="a", unity="km²", widget="pie"):
    widgetCompute = WidgetCompute.objects.create(axis1=axis1, axis2=axis2, indicator=ind, groupAxis1=json.dumps(grAx1), groupAxis2=json.dumps(grAx2), percent=percent)
    return WidgetParams.objects.create(title=title, subTitle=subTitle, position=pos, unity=unity, widget=cls.__dictWidget[widget], widgetCompute=widgetCompute)