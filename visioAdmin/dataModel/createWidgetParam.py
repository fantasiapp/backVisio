from visioServer.models import AxisForGraph, WidgetCompute, WidgetParams, Widget, Layout, LabelForGraph
import json

class CreateWidgetParam:
  __dictWidget = {}
  __colors = None
  __axis = None
  dictLayout = None
  dashboards = {
      "geo":{
        "Marché P2CD":["column:2:1", "Marché P2CD négoce, exprimé en milliers de km²"],
        "Marché Enduit":["column:2:1", "Le marché Enduit est reconstitué à partir des estimations P2CD FdV x un ratio théorique de 360 g/m²."],
        "PdM P2CD":["column:2:1", ""],
        "PdM Enduit":["column:2:1", ""],
        "PdM P2CD Simulation":["column:2:1", "Objectif Siège : @Nb, @GeoName : @Nb2 en km² \r\n Ciblage : @Nb3 en km²"],
        "PdM Enduit Simulation":["column:2:1", ""],
        "DN P2CD":["column:2:1", "Un client est un PdV où la part de marché Siniat est > 10%,\r\nLes zones grises correspondent aux PdV non documentés"],
        "DN Enduit":["column:2:1", ""],
        "DN P2CD Simulation":["column:2:1", "Objectif Siège : @Nb, @GeoName : @Nb2 en km² \r\n Ciblage : @Nb3 en km²"],
        "DN Enduit Simulation":["column:2:1", ""],
        "Points de Vente P2CD":["mono", ""],
        "Points de Vente Enduit":["mono", ""],
        "Synthèse P2CD":["row:1:1:1", ""],
        "Synthèse Enduit":["row:1:1:1", ""],
        "Synthèse P2CD Simulation":["row:1:1:1", ""],
        "Synthèse Enduit Simulation":["row:1:1:1", ""],
        "Suivi AD":["row:2:1", ""],
        "Suivi des Visites":["row:2:2", ""]},
      "trade":{
        "Marché P2CD Enseigne":["column:2:1", ""],
        "Marché Enduit Enseigne":["column:2:1", ""],
        "PdM P2CD Enseigne":["column:2:1", ""],
        "PdM Enduit Enseigne":["column:2:1", ""]}
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
      for name in ["pie", "donut", "image", "histoRow", "histoColumn", "histoColumnTarget", "table", "pieTarget", "gauge"]:
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
    if not cls.__colors:
      cls.__colors={}
      data = [
        ["segment", "Généralistes", "#888888"],
        ["segment", "Multi Spécialistes", "#E1962A"],
        ["segment", "Purs Spécialistes", "#DEDEDE"],
        ["segment", "Autres", "#DC6206"],
        ["industry","Siniat", "#B3007E"],
        ["industry","Potentiel ciblé", "#CD77E2"],
        ["industry","Placo", "#0056A6"],
        ["industry","Knauf", "#67D0FF"],
        ["industry","Challengers", "#888888"],
        ["indFinition","Pregy", "#B3007E"],
        ["indFinition","Salsi", "#D00000"],
        ["indFinition","Croissance", "#DEDEDE"],
        ["indFinition","Cible Croissance", "#CD77E2"],
        ["indFinition","Conquête", "#466A50"],
        ["indFinition","Cible Conquête", "#5BB273"],
        ["dnFinition","P2CD + Enduit", "#B3007E"],
        ["dnFinition","Enduit hors P2CD", "#D00000"],
        ["dnFinition","Cible P2CD", "#AC0000"],
        ["dnFinition","Pur prospect", "#8B8B8B"],
        ["dnFinition","Cible Pur Prospect", "#DEDEDE"],
        ["clientProspect","Client", "#B3007E"],
        ["clientProspect","Potentiel ciblé", "#CD77E2"],
        ["clientProspect","Prospect", "#888888"],
        ["clientProspect","Non documenté", "#DEDEDE"]
      ]
      for list in data:
        label = LabelForGraph.objects.create(axisType=list[0], label=list[1], color=list[2])
        cls.__colors[f"{list[0]}:{list[1]}"] = label

      cls.__axis = {}
      listTypeAxis = set(listColor[0] for listColor in data)
      for typeAxis in listTypeAxis:
        listLabel = LabelForGraph.objects.filter(axisType = typeAxis)
        axis = AxisForGraph.objects.create(name= typeAxis)
        for label in listLabel:
          axis.labels.add(label)
        cls.__axis[typeAxis] = axis


  @classmethod
  def create(cls, name):
    dictParam = {
      "Marché P2CD":[
        ["segmentMarketing", "segmentCommercial", "p2cd", AxisForGraph.objects.get(name="segment").id, ["@other"], "no", "Vente en volume", "@sum"],
        ["segmentMarketing", "segmentCommercial", "dn", AxisForGraph.objects.get(name="segment").id, ["@other"], "no", "Nombre de Pdv", "@sum", "b", "Pdv", "donut"],
        ["enseigne", "industrie", "p2cd", [], AxisForGraph.objects.get(name="industry").id, "no", "Volume par enseigne", "", "c", "km²", "histoRow"]
      ], "Marché Enduit":[
        ["enduitIndustrie", "segmentCommercial", "enduit", AxisForGraph.objects.get(name="indFinition").id, ["@other"], "no", "Volume Total", "@sum", "a", "T"],
        ["segmentDnEnduit", "segmentCommercial", "dn", AxisForGraph.objects.get(name="dnFinition").id, ["@other"], "no", "Nombre de Pdv", "@sum", "b", "Pdv", "donut"],
        ["enseigne", "enduitIndustrie", "enduit", [], AxisForGraph.objects.get(name="indFinition").id, "no", "Volume par enseigne", "Tous segments", "c", "T", "histoRow"]
      ], "PdM P2CD":[
        ["industrie", "segmentMarketing", "p2cd", AxisForGraph.objects.get(name="industry").id, ["@other"], "classic", "Pdm Total", "", "a", "%"],
        ["industrie", "segmentMarketing", "p2cd", AxisForGraph.objects.get(name="industry").id, [], "cols", "Par segment", "", "b", "%", "histoColumn"],
        ["enseigne", "industrie", "p2cd", [], AxisForGraph.objects.get(name="industry").id, "classic", "Par Enseigne", "Tous segments", "c", "%", "histoRow"]
      ], "PdM Enduit":[
        ["enduitIndustrie", "segmentCommercial", "Enduit", AxisForGraph.objects.get(name="indFinition").id, ["@other"], "classic", "Pdm Total", "", "a", "%"],
        ["enduitIndustrie", "segmentMarketing", "Enduit", AxisForGraph.objects.get(name="indFinition").id, [], "cols", "Par segment", "", "b", "%", "histoColumn"],
        ["enseigne", "enduitIndustrie", "Enduit", [], AxisForGraph.objects.get(name="indFinition").id, "classic", "Par Enseigne", "", "c", "%", "histoRow"]
      ], "PdM P2CD Simulation":[
        ["industrieTarget", "segmentMarketing", "p2cd", AxisForGraph.objects.get(name="industry").id, ["@other"], "classic", "Par Industrie", "", "a", "%", "pieTarget"],
        ["industrieTarget", "segmentMarketing", "p2cd", AxisForGraph.objects.get(name="industry").id, [], "cols", "Par segment", "", "b", "%", "histoColumn"],
        ["enseigne", "industrieTarget", "p2cd", [], AxisForGraph.objects.get(name="industry").id, "classic", "Par Enseigne", "Tous segments", "c", "%", "histoRow"]
      ], "PdM Enduit Simulation":[
        ["enduitIndustrieTarget", "segmentCommercial", "Enduit", AxisForGraph.objects.get(name="indFinition").id, ["@other"], "classic", "Pdm Total", "", "a", "%", "pieTarget"],
        ["enduitIndustrieTarget", "segmentMarketing", "Enduit", AxisForGraph.objects.get(name="indFinition").id, [], "cols", "Par segment", "", "b", "%", "histoColumn"],
        ["enseigne", "enduitIndustrieTarget", "Enduit", [], AxisForGraph.objects.get(name="indFinition").id, "classic", "Par Enseigne", "", "c", "%", "histoRow"]
      ], "DN P2CD":[
        ["clientProspect", "segmentMarketing", "dn", AxisForGraph.objects.get(name="clientProspect").id, ["@other"], "no", "Par Segment", "Nombre de Pdv Client/Prospect", "a", "Pdv", "donut"],
        ["clientProspect", "segmentMarketing", "dn", AxisForGraph.objects.get(name="clientProspect").id, [], "no", "Par Client et Prospect", "", "b", "Pdv", "histoColumn"],
        ["enseigne", "clientProspect", "dn", [], AxisForGraph.objects.get(name="clientProspect").id, "no", "Par Enseigne", "Tous Segments", "c", "Pdv", "histoRow"]
      ], "DN Enduit":[
        ["segmentDnEnduit", "segmentCommercial", "dn", AxisForGraph.objects.get(name="dnFinition").id, ["@other"], "no", "DN totale", "", "a", "Pdv", "donut"],
        ["segmentDnEnduit", "segmentMarketing", "dn", AxisForGraph.objects.get(name="dnFinition").id, [], "no", "Par segment", "", "b", "Pdv", "histoColumn"],
        ["enseigne", "segmentDnEnduit", "dn", [], AxisForGraph.objects.get(name="dnFinition").id, "no", "Par Enseigne", "Tous Segments", "c", "Pdv", "histoRow"]
      ], "DN P2CD Simulation":[
        ["clientProspectTarget", "segmentCommercial", "dn", AxisForGraph.objects.get(name="clientProspect").id, ["@other"], "no", "Par Client et Prospect", "", "a", "Pdv", "pieTarget"],
        ["clientProspectTarget", "segmentMarketing", "dn", AxisForGraph.objects.get(name="clientProspect").id, [], "no", "Par Segment", "", "b", "Pdv", "histoColumn"],
        ["enseigne", "clientProspectTarget", "dn", [], AxisForGraph.objects.get(name="clientProspect").id, "no", "Par Enseigne", "Tous Segments", "c", "Pdv", "histoRow"]
      ], "DN Enduit Simulation":[
        ["segmentDnEnduitTarget", "segmentCommercial", "dn", AxisForGraph.objects.get(name="dnFinition").id, ["@other"], "no", "DN totale", "", "a", "Pdv", "donut"],
        ["segmentDnEnduitTarget", "segmentMarketing", "dn", AxisForGraph.objects.get(name="dnFinition").id, [], "no", "Par segment", "", "b", "Pdv", "histoColumn"],
        ["enseigne", "segmentDnEnduitTarget", "dn", [], AxisForGraph.objects.get(name="dnFinition").id, "no", "Par Enseigne", "Tous Segments", "c", "Pdv", "histoRow"]
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
        ["industrieTarget", "lg-1", "P2CD", ["Siniat", "Potentiel Ciblé", "Concurrence"], [], "no", "", "", "a", "km²", "histoColumnTarget"],
        ["industrieTarget", "lg-1", "P2CD", ["Siniat", "Potentiel Ciblé", "Placo", "Knauf", "Challengers"], [], "cols", "", "", "b", "%", "histoColumn"],
        ["clientProspectTarget", "lg-1", "dn", [], [], "no", "", "", "c", "Pdv", "histoColumnTarget"]
      ], "Synthèse Enduit Simulation":[
        ["enduitIndustrieTarget", "lg-1", "enduit", [], [], "no", "Volume", "", "a", "T", "histoColumnTarget"],
        ["enduitIndustrieTarget", "lg-1", "enduit", [], [], "cols", "Pdm", "", "b", "%", "histoColumn"],
        ["segmentDnEnduitTarget", "lg-1", "dn", [], [], "no", "DN", "", "c", "Pdv", "histoColumn"]
      ], 'Suivi des Visites':[
        ["segmentMarketing", "segmentCommercial", "p2cd", [], ["@other"], "no", "Vente en volume", "", "a", "", "gauge"],
        ["segmentMarketing", "segmentCommercial", "dn", [], ["@other"], "no", "Nombre de Pdv", "", "", "b", "gauge"],
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
    if params == "Synthèse Enduit Simulation": print("done", params, name)
    paramName = ["axis1", "axis2", "ind", "grAx1", "grAx2", "percent", "title", "subTitle", "pos", "unity", "widget"]
    return [cls.executeCreation(**{paramName[i]:param[i] for i in range(len(param))}) for param in params]

  @classmethod
  def executeCreation(cls, axis1, axis2, ind, grAx1, grAx2, percent=False, title="Titre", subTitle="", pos="a", unity="km²", widget="pie"):
    widgetCompute = WidgetCompute.objects.create(axis1=axis1, axis2=axis2, indicator=ind, groupAxis1=json.dumps(grAx1), groupAxis2=json.dumps(grAx2), percent=percent)
    return WidgetParams.objects.create(title=title, subTitle=subTitle, position=pos, unity=unity, widget=cls.__dictWidget[widget], widgetCompute=widgetCompute)