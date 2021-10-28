from visioServer.models import AxisForGraph, WidgetCompute, WidgetParams, Widget, Layout, LabelForGraph, ParamVisio
import json

class CreateWidgetParam:
  __dictWidget = {}
  __colors = None
  __axis = None
  dictLayout = None
  rf = str(int(ParamVisio.getValue("ratioPlaqueFinition") * 1000))
  dashBoardsList = {
    "geo":[
      ["Marché P2CD","column:2:1", "Marché P2CD négoce, exprimé en milliers de km²."],
      ["Marché Enduit","column:2:1", f"Le marché Enduit est reconstitué à partir des estimations P2CD FdV x un ratio théorique de {rf} g/m²."],
      ["PdM P2CD","column:2:1", ""],
      ["PdM Enduit","column:2:1", ""],
      ["PdM P2CD Simulation","column:2:1", ["@objectifSiege", "@DRV", "@objectifP2CD", "@ciblageP2CD"]],
      ["PdM Enduit Simulation","column:2:1", ["@objectifEnduit","@ciblageEnduit"]],
      ["DN P2CD","column:2:1", "Un client est un PdV où la part de marché Siniat est > 10%,\r\nLes zones grises correspondent aux PdV non documentés"],
      ["DN Enduit","column:2:1", ""],
      ["DN P2CD Simulation","column:2:1", ["@objectifSiegeDn", "@DRVdn", "@objectifP2CDdn", "@ciblageP2CDdn"]],
      ["Points de Vente P2CD","mono", ""],
      ["Points de Vente Enduit","mono", ""],
      ["Synthèse P2CD","row:1:1:1", ""],
      ["Synthèse Enduit","row:1:1:1", ""],
      ["Synthèse P2CD Simulation","row:1:1:1", []],
      ["Synthèse Enduit Simulation","row:1:1:1", ""],
      ["Suivi AD","row:2:1", ""],
      ["Suivi des Visites","row:2:2", ""],
    ], "trade":[
      ["Marché P2CD","column:2:1", "Marché P2CD négoce, exprimé en milliers de km²"],
      ["Marché Enduit","column:2:1", f"Le marché Enduit est reconstitué à partir des estimations P2CD FdV x un ratio théorique de {rf} g/m²."],#19
      ["PdM P2CD","column:2:1", ""],#20
      ["PdM Enduit","column:2:1", ""],
      ["DN P2CD","column:2:1", "Un client est un PdV où la part de marché Siniat est > 10%,\r\nLes zones grises correspondent aux PdV non documentés"],#21
      ["DN Enduit","column:2:1", ""],#22
      ["Points de Vente P2CD","mono", ""],#23
      ["Points de Vente Enduit","mono", ""],#24
      ["Synthèse P2CD","row:1:1:1", ""],#25
      ["Synthèse Enduit","row:1:1:1", ""],#26
    ]
  }
  dashboardsLevel = {
    "geo":{"root":["Marché P2CD", "Marché Enduit", "PdM P2CD", "PdM Enduit", "PdM P2CD Simulation", "PdM Enduit Simulation", "DN P2CD", "DN Enduit",
    "DN P2CD Simulation", "Points de Vente P2CD", "Points de Vente Enduit", "Synthèse P2CD", "Synthèse Enduit",
    "Synthèse P2CD Simulation", "Synthèse Enduit Simulation", "Suivi AD", "Suivi des Visites"],

    "drv":["Marché P2CD", "Marché Enduit", "PdM P2CD", "PdM Enduit", "PdM P2CD Simulation", "PdM Enduit Simulation", "DN P2CD", "DN Enduit",
    "DN P2CD Simulation", "Points de Vente P2CD", "Points de Vente Enduit", "Synthèse P2CD",
    "Synthèse P2CD Simulation", "Suivi AD", "Suivi des Visites"],

    "agent":["Marché P2CD", "Marché Enduit", "PdM P2CD", "PdM Enduit", "PdM P2CD Simulation", "PdM Enduit Simulation", "DN P2CD", "DN P2CD Simulation",
    "DN Enduit", "Points de Vente P2CD", "Points de Vente Enduit"],

    "agentFinitions":["Marché P2CD", "Marché Enduit", "PdM P2CD", "PdM Enduit", "PdM Enduit Simulation", "DN P2CD", "DN Enduit", "Points de Vente P2CD",
    "Points de Vente Enduit", "Suivi des Visites"],

    "dep":["Marché P2CD", "Marché Enduit", "PdM P2CD", "PdM Enduit", "DN P2CD", "DN Enduit", "Points de Vente P2CD", "Points de Vente Enduit"],

    "bassin":["Marché P2CD", "Marché Enduit", "PdM P2CD", "PdM Enduit", "DN P2CD", "DN Enduit", "Points de Vente P2CD", "Points de Vente Enduit"]
    },
    "trade":{
      "root":["Marché P2CD", "Marché Enduit", "PdM P2CD", "PdM Enduit", "DN P2CD", "DN Enduit",
      "Points de Vente P2CD", "Points de Vente Enduit", "Synthèse P2CD", "Synthèse Enduit"],

      "enseigne":["Marché P2CD", "Marché Enduit", "PdM P2CD", "PdM Enduit", "DN P2CD", "DN Enduit",
      "Points de Vente P2CD", "Points de Vente Enduit", "Synthèse P2CD", "Synthèse Enduit"],

      "ensemble":["Marché P2CD", "Marché Enduit", "PdM P2CD", "PdM Enduit", "DN P2CD", "DN Enduit",
      "Points de Vente P2CD", "Points de Vente Enduit", "Synthèse P2CD", "Synthèse Enduit"],

      "sousEnsemble":["Marché P2CD", "Marché Enduit", "PdM P2CD", "PdM Enduit", "DN P2CD", "DN Enduit",
      "Points de Vente P2CD", "Points de Vente Enduit", "Synthèse P2CD", "Synthèse Enduit"]}
    }
  

  @classmethod
  def initialize(cls):
    if not cls.__dictWidget:
      for name in ["pie", "donut", "image", "histoRow", "histoColumn", "histoColumnTarget", "table", "pieTarget", "gauge", "histoCurve"]:
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
        ["segment", "Purs Spécialistes", "#DEDEDE"],
        ["segment", "Multi Spécialistes", "#E1962A"],
        ["segment", "Généralistes", "#888888"],
        ["segment", "Autres", "#DC6206"],

        ["industry","Siniat", "#B3007E"],
        ["industry","Placo", "#0056A6"],
        ["industry","Knauf", "#67D0FF"],
        ["industry","Challengers", "#888888"],

        ["industryP2CD","Siniat", "#B3007E"],
        ["industryP2CD","Placo", "#0056A6"],
        ["industryP2CD","Knauf", "#67D0FF"],
        ["industryP2CD","Isolava", "#888888"],
        ["industryP2CD","Fassa", "#888888"],
        ["industryP2CD","Rockwool", "#888888"],
        ["industryP2CD","Efisol", "#888888"],
        ["industryP2CD","Semin", "#888888"],
        ["industryP2CD","Gyproc", "#888888"],
        ["industryP2CD","MDD", "#888888"],
        ["industryP2CD","Deltisol", "#888888"],
        ["industryP2CD","Sopreba", "#888888"],
        ["industryP2CD","Norgyps", "#888888"],
        ["industryP2CD","Pladur", "#888888"],
        ["industryP2CD","IsoVer", "#888888"],

        ["industryTarget","Siniat", "#B3007E"],
        ["industryTarget","Potentiel ciblé", "#CD77E2"],
        ["industryTarget","Placo", "#0056A6"],
        ["industryTarget","Knauf", "#67D0FF"],
        ["industryTarget","Challengers", "#888888"],

        ["indFinition","Prégy", "#B3007E"],
        ["indFinition","Salsi", "#D00000"],
        ["indFinition","Croissance", "#DEDEDE"],
        ["indFinition","Conquête", "#466A50"],

        ["indFinitionTarget","Prégy", "#B3007E"],
        ["indFinitionTarget","Salsi", "#D00000"],
        ["indFinitionTarget","Cible Croissance", "#CD77E2"],
        ["indFinitionTarget","Cible Conquête", "#5BB273"],
        ["indFinitionTarget","Croissance", "#DEDEDE"],
        ["indFinitionTarget","Conquête", "#466A50"],

        ["dnFinition","P2CD + Enduit", "#B3007E"],
        ["dnFinition","Enduit hors P2CD", "#AC0000"],
        ["dnFinition","Pur prospect", "#8B8B8B"],
        ["dnFinition","Non documenté", "#DEDEDE"],

        ["dnFinitionTarget","P2CD + Enduit", "#B3007E"],
        ["dnFinitionTarget","Enduit hors P2CD", "#AC0000"],
        ["dnFinitionTarget","Cible P2CD", "#D00000"],
        ["dnFinitionTarget","Cible Pur Prospect", "#DEDEDE"],
        ["dnFinitionTarget","Pur prospect", "#8B8B8B"],
        ["dnFinitionTarget","Non documenté", "#DEDEDE"],

        ["dnFinitionTargetVisits","P2CD + Enduit", "#B3007E"],
        ["dnFinitionTargetVisits","Cible P2CD + Enduit", "#CD77E2"],
        ["dnFinitionTargetVisits","Enduit hors P2CD", "#AC0000"],
        ["dnFinitionTargetVisits","Cible Enduit hors P2CD", "#D00000"],
        ["dnFinitionTargetVisits","Pur prospect", "#8B8B8B"],
        ["dnFinitionTargetVisits","Cible Pur Prospect", "#DEDEDE"],

        ["clientProspect","Client", "#B3007E"],
        ["clientProspect","Prospect", "#888888"],
        ["clientProspect","Non documenté", "#DEDEDE"],

        ["clientProspectTarget","Client", "#B3007E"],
        ["clientProspectTarget","Potentiel ciblé", "#CD77E2"],
        ["clientProspectTarget","Prospect", "#888888"],
        ["clientProspectTarget","Non documenté", "#DEDEDE"],

        ["suiviAD","Non renseignées", "#D00000"],
        ["suiviAD","Non mises à jour", "#FFE200"],
        ["suiviAD","Terminées", "#4AA763"],

        ["histo&curve","Nombre de PdV complétés", "#363565"],
        ["histo&curve","Cumul en pourcentage", "#F06D0C"]
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
  def create(cls, name, geoOrTrade):
    dictParam = {
      "geo":{
      "Marché P2CD":[
        ["segmentMarketing", "segmentCommercial", "p2cd", AxisForGraph.objects.get(name="segment").id, ["@other"], "no", "Volume de vente par segment", "@sum"],
        ["segmentMarketing", "segmentCommercial", "dn", AxisForGraph.objects.get(name="segment").id, ["@other"], "no", "Nombre de points de vente par segment", "@sum", "b", "PdV", "donut"],
        ["enseigne", "industrie", "p2cd", [], AxisForGraph.objects.get(name="industry").id, "no", "Volume de vente par enseigne", "Tous segments", "c", "km²", "histoRow"]
      ], "Marché Enduit":[
        ["enduitIndustrie", "segmentCommercial", "enduit", AxisForGraph.objects.get(name="indFinition").id, ["@other"], "no", "Volume de vente", "@sum", "a", "T"],
        ["segmentDnEnduit", "segmentCommercial", "dn", AxisForGraph.objects.get(name="dnFinition").id, ["@other"], "no", "Nombre de points de vente", "@sum", "b", "PdV", "donut"],
        ["enseigne", "enduitIndustrie", "enduit", [], AxisForGraph.objects.get(name="indFinition").id, "no", "Volume de vente par enseigne", "Tous segments", "c", "T", "histoRow"]
      ], "PdM P2CD":[
        ["industrie", "segmentMarketing", "p2cd", AxisForGraph.objects.get(name="industry").id, ["@other"], "classic", "Parts de marché par industrie", "", "a", "%"],
        ["industrie", "segmentMarketing", "p2cd", AxisForGraph.objects.get(name="industry").id, [], "cols", "Parts de marché par segment", "", "b", "%", "histoColumn"],
        ["enseigne", "industrie", "p2cd", [], AxisForGraph.objects.get(name="industry").id, "classic", "Parts de marché par enseigne", "Tous segments", "c", "%", "histoRow"]
      ], "PdM Enduit":[
        ["enduitIndustrie", "segmentCommercial", "Enduit", AxisForGraph.objects.get(name="indFinition").id, ["@other"], "classic", "Parts de marché par industrie", "", "a", "%"],
        ["enduitIndustrie", "segmentMarketing", "Enduit", AxisForGraph.objects.get(name="indFinition").id, [], "cols", "Parts de marché par segment", "", "b", "%", "histoColumn"],
        ["enseigne", "enduitIndustrie", "Enduit", [], AxisForGraph.objects.get(name="indFinition").id, "classic", "Parts de marché par enseigne", "Tous segments", "c", "%", "histoRow"]
      ], "PdM P2CD Simulation":[
        ["industrieTarget", "segmentMarketing", "p2cd", AxisForGraph.objects.get(name="industryTarget").id, ["@other"], "classic", "Parts de marché par industrie", "", "a", "%", "pieTarget"],
        ["industrieTarget", "segmentMarketing", "p2cd", AxisForGraph.objects.get(name="industryTarget").id, [], "cols", "Parts de marché par segment", "", "b", "%", "histoColumn"],
        ["enseigne", "industrieTarget", "p2cd", [], AxisForGraph.objects.get(name="industryTarget").id, "classic", "Parts de marché par enseigne", "Tous segments", "c", "%", "histoRow"]
      ], "PdM Enduit Simulation":[
        ["enduitIndustrieTarget", "segmentCommercial", "Enduit", AxisForGraph.objects.get(name="indFinitionTarget").id, ["@other"], "classic", "Parts de marché par industrie", "", "a", "%", "pieTarget"],
        ["enduitIndustrieTarget", "segmentMarketing", "Enduit", AxisForGraph.objects.get(name="indFinitionTarget").id, [], "cols", "Parts de marché par segment", "", "b", "%", "histoColumn"],
        ["enseigne", "enduitIndustrieTarget", "Enduit", [], AxisForGraph.objects.get(name="indFinitionTarget").id, "classic", "Parts de marché par enseigne", "Tous segments", "c", "%", "histoRow"]
      ], "DN P2CD":[
        ["clientProspect", "segmentMarketing", "dn", AxisForGraph.objects.get(name="clientProspect").id, ["@other"], "no", "DN totale", "@sum", "a", "PdV", "donut"],
        ["clientProspect", "segmentMarketing", "dn", AxisForGraph.objects.get(name="clientProspect").id, [], "no", "DN par segment", "", "b", "PdV", "histoColumn"],
        ["enseigne", "clientProspect", "dn", [], AxisForGraph.objects.get(name="clientProspect").id, "no", "DN par enseigne", "Tous segments", "c", "PdV", "histoRow"]
      ], "DN Enduit":[
        ["segmentDnEnduit", "segmentCommercial", "dn", AxisForGraph.objects.get(name="dnFinition").id, ["@other"], "no", "DN totale", "@sum", "a", "PdV", "donut"],
        ["segmentDnEnduit", "segmentMarketing", "dn", AxisForGraph.objects.get(name="dnFinition").id, [], "no", "DN par segment", "", "b", "PdV", "histoColumn"],
        ["enseigne", "segmentDnEnduit", "dn", [], AxisForGraph.objects.get(name="dnFinition").id, "no", "DN par enseigne", "Tous segments", "c", "PdV", "histoRow"]
      ], "DN P2CD Simulation":[
        ["clientProspectTarget", "segmentCommercial", "dn", AxisForGraph.objects.get(name="clientProspectTarget").id, ["@other"], "no", "DN totale", "@sum", "a", "PdV", "pieTarget"],
        ["clientProspectTarget", "segmentMarketing", "dn", AxisForGraph.objects.get(name="clientProspectTarget").id, [], "no", "DN par Segment", "", "b", "PdV", "histoColumn"],
        ["enseigne", "clientProspectTarget", "dn", [], AxisForGraph.objects.get(name="clientProspectTarget").id, "no", "DN par enseigne", "Tous segments", "c", "PdV", "histoRow"]
      ], "Points de Vente P2CD":[
        ["pdvs", "colTableP2cd", "p2cd", [], [], "no", "@titleTableP2cd", "", "a", "m²", "table"]
      ], "Points de Vente Enduit":[
        ["pdvs", "colTableEnduit", "enduit", [], [], "no", "@titleTableEnduit", "", "a", "T", "table"]
      ], "Synthèse P2CD":[
        ["industrie", "lg-1", "P2CD", AxisForGraph.objects.get(name="industry").id, [], "no", "Volume de vente par division géographique", "", "a", "km²", "histoColumn"],
        ["industrie", "lg-1", "P2CD", AxisForGraph.objects.get(name="industry").id, [], "cols", "Parts de marché par division géographique", "", "b", "%", "histoColumn"],
        ["clientProspect", "lg-1", "dn", AxisForGraph.objects.get(name="clientProspect").id, [], "no", "DN par division géographique", "", "c", "PdV", "histoColumn"]
      ], "Synthèse Enduit":[
        ["enduitIndustrie", "agentFinitions", "enduit", AxisForGraph.objects.get(name="indFinition").id, [], "no", "Volume de vente par division géographique", "", "a", "T", "histoColumn"],
        ["enduitIndustrie", "agentFinitions", "enduit", AxisForGraph.objects.get(name="indFinition").id, [], "cols", "Parts de marché par division géographique", "", "b", "%", "histoColumn"],
        ["segmentDnEnduit", "agentFinitions", "dn", AxisForGraph.objects.get(name="dnFinition").id, [], "no", "DN par division géographique", "", "c", "PdV", "histoColumn"]
      ], "Synthèse P2CD Simulation":[
        ["industrieTarget", "lg-1", "P2CD", AxisForGraph.objects.get(name="industryTarget").id, [], "no", "Volume de vente par division géographique", "", "a", "km²", "histoColumnTarget"],
        ["industrieTarget", "lg-1", "P2CD", AxisForGraph.objects.get(name="industryTarget").id, [], "cols", "Parts de marché par division géographique", "", "b", "%", "histoColumn"],
        ["clientProspectTarget", "lg-1", "dn", AxisForGraph.objects.get(name="clientProspectTarget").id, [], "no", "DN par division géographique", "", "c", "PdV", "histoColumnTarget"]
      ], "Synthèse Enduit Simulation":[
        ["enduitIndustrieTarget", "agentFinitions", "enduit", AxisForGraph.objects.get(name="indFinitionTarget").id, [], "no", "Volume de vente par division géographique", "", "a", "T", "histoColumnTarget"],
        ["enduitIndustrieTarget", "agentFinitions", "enduit", AxisForGraph.objects.get(name="indFinitionTarget").id, [], "cols", "Parts de marché par division géographique", "", "b", "%", "histoColumn"],
        ["segmentDnEnduitTarget", "agentFinitions", "dn", AxisForGraph.objects.get(name="dnFinitionTarget").id, [], "no", "DN par division géographique", "", "c", "PdV", "histoColumn"]
      ], "Suivi AD":[
        ["avancementAD", "segmentCommercial", "p2cd", [], ["@other"], "no", "Avancement de l'AD", "", "a", "", "gauge"],
        ["histo&curve", "weeks", "dn", AxisForGraph.objects.get(name="histo&curve").id, [], "no", "Évolution de l'AD au cours des dernières semaines", "", "b", "%|PdV", "histoCurve"],
        ["suiviAD", "lg-1", "dn", AxisForGraph.objects.get(name="suiviAD").id, [], "cols", "Avancement de l'AD par division géographique", "", "c", "%", "histoColumn"]
      ], 'Suivi des Visites':[
        ["visits", "segmentCommercial", "p2cd", [], ["@other"], "no", "Avancée des visites", "", "a", "", "gauge"],
        ["targetedVisits", "segmentCommercial", "dn", [], ["@other"], "no", "Proportion de visites ciblées", "", "b", "", "gauge"],
        ['segmentDnEnduitTargetVisits', "segmentMarketing", "enduit", AxisForGraph.objects.get(name="dnFinitionTargetVisits").id, ["@other"], "no", "Répartition des visites en volume", "@sum", "c", "T"],
        ['segmentDnEnduitTargetVisits', "segmentMarketing", "visits", AxisForGraph.objects.get(name="dnFinitionTargetVisits").id, ["@other"], "no", "Répartition des visites en DN", "@sum", "d", "visites"]
      ]
      }, "trade":{
      "Marché P2CD":[
        ["segmentMarketing", "segmentCommercial", "p2cd", AxisForGraph.objects.get(name="segment").id, ["@other"], "no", "Volume de vente par segment", "@sum"],
        ["segmentMarketing", "segmentCommercial", "dn", AxisForGraph.objects.get(name="segment").id, ["@other"], "no", "Nombre de points de vente par segment", "@sum", "b", "PdV", "donut"],
        ["lt-1", "industrie", "p2cd", [], AxisForGraph.objects.get(name="industry").id, "no", "Volume de vente par enseigne", "Tous segments", "c", "km²", "histoRow"]
      ], "Marché Enduit":[
        ["enduitIndustrie", "segmentCommercial", "enduit", AxisForGraph.objects.get(name="indFinition").id, ["@other"], "no", "Volume de vente", "@sum", "a", "T"],
        ["segmentDnEnduit", "segmentCommercial", "dn", AxisForGraph.objects.get(name="dnFinition").id, ["@other"], "no", "Nombre de points de vente", "@sum", "b", "PdV", "donut"],
        ["lt-1", "enduitIndustrie", "enduit", [], AxisForGraph.objects.get(name="indFinition").id, "no", "Volume de vente par enseigne", "Tous segments", "c", "T", "histoRow"]
      ], "PdM P2CD":[
        ["industrie", "segmentMarketing", "p2cd", AxisForGraph.objects.get(name="industry").id, ["@other"], "classic", "Parts de marché par industrie", "", "a", "%"],
        ["industrie", "segmentMarketing", "p2cd", AxisForGraph.objects.get(name="industry").id, [], "cols", "Parts de marché par segment", "", "b", "%", "histoColumn"],
        ["lt-1", "industrie", "p2cd", [], AxisForGraph.objects.get(name="industry").id, "classic", "Parts de marché par enseigne", "Tous segments", "c", "%", "histoRow"]
      ], "PdM Enduit":[
        ["enduitIndustrie", "segmentCommercial", "Enduit", AxisForGraph.objects.get(name="indFinition").id, ["@other"], "classic", "Parts de marché par industrie", "", "a", "%"],
        ["enduitIndustrie", "segmentMarketing", "Enduit", AxisForGraph.objects.get(name="indFinition").id, [], "cols", "Parts de marché par segment", "", "b", "%", "histoColumn"],
        ["lt-1", "enduitIndustrie", "Enduit", [], AxisForGraph.objects.get(name="indFinition").id, "classic", "Parts de marché par enseigne", "Tous segments", "c", "%", "histoRow"]
      ],"DN P2CD":[
        ["clientProspect", "segmentMarketing", "dn", AxisForGraph.objects.get(name="clientProspect").id, ["@other"], "no", "DN totale", "@sum", "a", "PdV", "donut"],
        ["clientProspect", "segmentMarketing", "dn", AxisForGraph.objects.get(name="clientProspect").id, [], "no", "DN par segment", "", "b", "PdV", "histoColumn"],
        ["lt-1", "clientProspect", "dn", [], AxisForGraph.objects.get(name="clientProspect").id, "no", "DN par enseigne", "Tous segments", "c", "PdV", "histoRow"]
      ], "DN Enduit":[
        ["segmentDnEnduit", "segmentCommercial", "dn", AxisForGraph.objects.get(name="dnFinition").id, ["@other"], "no", "DN totale", "@sum", "a", "PdV", "donut"],
        ["segmentDnEnduit", "segmentMarketing", "dn", AxisForGraph.objects.get(name="dnFinition").id, [], "no", "DN par segment", "", "b", "PdV", "histoColumn"],
        ["lt-1", "segmentDnEnduit", "dn", [], AxisForGraph.objects.get(name="dnFinition").id, "no", "DN par enseigne", "Tous segments", "c", "PdV", "histoRow"]
      ],"Points de Vente P2CD":[
        ["pdvs", "colTableP2cd", "p2cd", [], [], "no", "@titleTableP2cd", "", "a", "m²", "table"]
      ], "Points de Vente Enduit":[
        ["pdvs", "colTableEnduit", "enduit", [], [], "no", "@titleTableEnduit", "", "a", "T", "table"]
      ], "Synthèse P2CD":[
        ["industrie", "lgp-1", "P2CD", AxisForGraph.objects.get(name="industry").id, [], "no", "Volume de vente par division géographique", "", "a", "km²", "histoColumn"],
        ["industrie", "lgp-1", "P2CD", AxisForGraph.objects.get(name="industry").id, [], "cols", "Parts de marché par division géographique", "", "b", "%", "histoColumn"],
        ["clientProspect", "lgp-1", "dn", AxisForGraph.objects.get(name="clientProspect").id, [], "no", "DN par division géographique", "", "c", "PdV", "histoColumn"]
      ], "Synthèse Enduit":[
        ["enduitIndustrie", "agentFinitions", "enduit", AxisForGraph.objects.get(name="indFinition").id, [], "no", "Volume de vente par division géographique", "", "a", "T", "histoColumn"],
        ["enduitIndustrie", "agentFinitions", "enduit", AxisForGraph.objects.get(name="indFinition").id, [], "cols", "Parts de marché par division géographique", "", "b", "%", "histoColumn"],
        ["segmentDnEnduit", "agentFinitions", "dn", AxisForGraph.objects.get(name="dnFinition").id, [], "no", "DN par division géographique", "", "c", "PdV", "histoColumn"]
      ], 
      'other':[
        ["segmentMarketing", "segmentCommercial", "p2cd", [], ["@other"], "no", "Vente en volume"],
        ["segmentMarketing", "segmentCommercial", "dn", [], ["@other"], "no", "Nombre de PdV", "", "b"],
        ["enseigne", "industrie", "p2cd", [], ["Siniat", "Placo", "Knauf", "Challengers"], "no", "Volume par enseigne", "", "c", "histoRow"],
        ["enseigne", "industrie", "dn", [], ["Siniat", "Placo", "Knauf", "Challengers"], "no", "Volume par industrie", "Tous segments", "c", "histoColumn"]
      ]
      }
    }
    params = dictParam[geoOrTrade][name] if name in dictParam[geoOrTrade] else dictParam['trade']['other']
    paramName = ["axis1", "axis2", "ind", "grAx1", "grAx2", "percent", "title", "subTitle", "pos", "unity", "widget"]
    return [cls.executeCreation(**{paramName[i]:param[i] for i in range(len(param))}) for param in params]

  @classmethod
  def executeCreation(cls, axis1, axis2, ind, grAx1, grAx2, percent=False, title="Titre", subTitle="", pos="a", unity="km²", widget="pie"):
    widgetCompute = WidgetCompute.objects.create(axis1=axis1, axis2=axis2, indicator=ind, groupAxis1=json.dumps(grAx1), groupAxis2=json.dumps(grAx2), percent=percent)
    subTitle = json.dumps(subTitle) if isinstance(subTitle, list) else json.dumps([subTitle])
    return WidgetParams.objects.create(title=title, subTitle=subTitle, position=pos, unity=unity, widget=cls.__dictWidget[widget], widgetCompute=widgetCompute)
