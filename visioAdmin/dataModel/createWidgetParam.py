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
      for name in ["pie", "donut", "image", "histoRow", "histoColumn", "table"]:
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
        ["segmentMarketing", "segmentCommercial", "p2cd", [], ["@other"], False, "Vente en volume"],
        ["segmentMarketing", "segmentCommercial", "dn", [], ["@other"], False, "Nombre de Pdv", "", "b"],
        ["enseigne", "industrie", "p2cd", [], ["Siniat", "Placo", "Knauf", "@other"], False, "Volume par enseigne", "", "c", "histoRow"]
      ], "Marché Enduit":[
        ["enduitIndustrie", "segmentCommercial", "p2cd", [], ["@other"], False, "Volume Total"],
        ["segmentMarketing", "segmentCommercial", "dn", [], ["@other"], False, "Nombre de Pdv", "", "b"],
        ["enseigne", "segmentCommercial", "p2cd", [], ["Siniat", "Placo", "Knauf", "@other"], False, "Volume par enseigne", "", "c", "histoRow"]
      ], "PdM P2CD":[
        ["industrie", "segmentMarketing", "p2cd", ["Siniat", "Placo", "Knauf", "@other"], ["@other"], True, "Volume par segment"],
        ["industrie", "segmentMarketing", "p2cd", ["Siniat", "Placo", "Knauf", "@other"], [], True, "Volume par segment", "", "b", "histoColumn"],
        ["enseigne", "industrie", "p2cd", [], ["Siniat", "Placo", "Knauf", "@other"], True, "Tous Segment", "", "c", "histoRow"]
      ], "PdM Enduit":[
        ["industrie", "segmentMarketing", "Enduit", ["Siniat", "Placo", "Knauf", "@other"], ["@other"], True, "Volume par segment"],
        ["industrie", "segmentMarketing", "Enduit", ["Siniat", "Placo", "Knauf", "@other"], [], True, "Volume par segment", "", "b", "histoColumn"],
        ["enseigne", "industrie", "Enduit", [], ["Siniat", "Placo", "Knauf", "@other"], True, "Tous Segment", "", "c", "histoRow"]
      ], "DN P2CD":[
        ["industrie", "segmentMarketing", "dn", ["Siniat", "Placo", "Knauf", "@other"], ["@other"], True, "Volume par segment"],
        ["industrie", "segmentMarketing", "dn", ["Siniat", "Placo", "Knauf", "@other"], [], True, "Volume par segment", "", "b", "histoColumn"],
        ["enseigne", "industrie", "dn", [], ["Siniat", "Placo", "Knauf", "@other"], True, "Tous Segment", "", "c", "histoRow"]
      ], "DN Enduit":[
        ["industrie", "segmentMarketing", "dn", ["Siniat", "Placo", "Knauf", "@other"], ["@other"], True, "Volume par segment"],
        ["industrie", "segmentMarketing", "dn", ["Siniat", "Placo", "Knauf", "@other"], [], True, "Volume par segment", "", "b", "histoColumn"],
        ["enseigne", "industrie", "dn", [], ["Siniat", "Placo", "Knauf", "@other"], True, "Tous Segment", "", "c", "histoRow"]
      ], "Point de Vente P2CD":[
        ["industrie", "segmentMarketing", "dn", ["Siniat", "Placo", "Knauf", "@other"], ["@other"], True, "table"]
      ], "Point de Vente Enduit":[
        ["industrie", "segmentMarketing", "dn", ["Siniat", "Placo", "Knauf", "@other"], ["@other"], True, "table"]
      ], "Synthèse P2CD":[
        ["industrie", "segmentMarketing", "P2CD", ["Siniat", "Placo", "Knauf", "@other"], [], False, "Volume par segment", "", "a", "histoColumn"],
        ["industrie", "segmentMarketing", "P2CD", ["Siniat", "Placo", "Knauf", "@other"], [], True, "Volume par segment", "", "b", "histoColumn"],
        ["enseigne", "segmentMarketing", "dn", ["Siniat", "Placo", "Knauf", "@other"], [], False, "Tous Segment", "", "c", "histoColumn"]
      ], "Synthèse Enduit":[
        ["industrie", "segmentMarketing", "dn", ["Siniat", "Placo", "Knauf", "@other"], [], False, "Volume par segment", "", "a", "histoColumn"],
        ["industrie", "segmentMarketing", "dn", ["Siniat", "Placo", "Knauf", "@other"], [], True, "Volume par segment", "", "b", "histoColumn"],
        ["enseigne", "segmentMarketing", "dn", ["Siniat", "Placo", "Knauf", "@other"], [], False, "Tous Segment", "", "c", "histoColumn"]
      ], "Synthèse P2CD Simulation":[
        ["industrie", "segmentMarketing", "P2CD", ["Siniat", "Placo", "Knauf", "@other"], [], False, "Volume par segment", "", "a", "histoColumn"],
        ["industrie", "segmentMarketing", "P2CD", ["Siniat", "Placo", "Knauf", "@other"], [], True, "Volume par segment", "", "b", "histoColumn"],
        ["enseigne", "segmentMarketing", "dn", ["Siniat", "Placo", "Knauf", "@other"], [], False, "Tous Segment", "", "c", "histoColumn"]
      ], 'Suivi des Visites':[
        ["segmentMarketing", "segmentCommercial", "p2cd", [], ["@other"], False, "Vente en volume"],
        ["segmentMarketing", "segmentCommercial", "dn", [], ["@other"], False, "Nombre de Pdv", "", "b"],
        ["segmentMarketing", "segmentCommercial", "p2cd", [], ["@other"], False, "Vente en volume", "", "c"],
        ["segmentMarketing", "segmentCommercial", "dn", [], ["@other"], False, "Nombre de Pdv", "", "d"],
      ], 'other':[
        ["segmentMarketing", "segmentCommercial", "p2cd", [], ["@other"], False, "Vente en volume"],
        ["segmentMarketing", "segmentCommercial", "dn", [], ["@other"], False, "Nombre de Pdv", "", "b"],
        ["enseigne", "industrie", "p2cd", [], ["Siniat", "Placo", "Knauf", "@other"], False, "Volume par enseigne", "", "c", "histoRow"],
        ["enseigne", "industrie", "dn", [], ["Siniat", "Placo", "Knauf", "@other"], False, "Volume par industrie", "", "c", "histoColumn"]
      ]
    }
    params = dictParam[name] if name in dictParam else dictParam['other']
    paramName = ["axis1", "axis2", "ind", "grAx1", "grAx2", "percent", "title", "subTitle", "pos", "widget"]

    return [cls.executeCreation(**{paramName[i]:param[i] for i in range(len(param))}) for param in params]

  @classmethod
  def executeCreation(cls, axis1, axis2, ind, grAx1, grAx2, percent=False, title="Titre", subTitle="", pos="a", widget="pie"):
    print("start", axis1, axis2, ind, grAx1, grAx2, percent, title, subTitle, pos)
    widgetCompute = WidgetCompute.objects.create(axis1=axis1, axis2=axis2, indicator=ind, groupAxis1=json.dumps(grAx1), groupAxis2=json.dumps(grAx2), percent=percent)
    print(axis1, axis2, ind, grAx1, grAx2, percent, title, subTitle, pos, widgetCompute, widget, cls.__dictWidget[widget])
    return WidgetParams.objects.create(title=title, subTitle=subTitle, position=pos, widget=cls.__dictWidget[widget], widgetCompute=widgetCompute)