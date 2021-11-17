from visioServer.models import AxisForGraph, WidgetCompute, WidgetParams, Widget, Layout, LabelForGraph, ParamVisio
import json

class CreateWidgetParam:
  __dictWidget = {}
  __colors = None
  __axis = None
  dictLayout = None
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
    rf = str(int(ParamVisio.getValue("ratioPlaqueFinition") * 1000))
    CreateWidgetParam.dashBoardsList = {
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
        ["Points de Vente Enduit","mono", ["@objectifEnduit", '@ciblageEnduitComplet']],
        ["Synthèse P2CD","row:1:1:1", ""],
        ["Synthèse Enduit","row:1:1:1", ""],
        ["Synthèse P2CD Simulation","row:1:1:1", []],
        ["Synthèse Enduit Simulation","row:1:1:1", ""],
        ["Suivi AD","row:2:1", ""],
        ["Suivi des Visites","row:2:2", ""],
      ],
      "trade":[
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
        ["segment", "Purs Spécialistes", "#DEDEDE", 0],
        ["segment", "Multi Spécialistes", "#E1962A", 1],
        ["segment", "Généralistes", "#888888", 2],
        ["segment", "Autres", "#DC6206", 3],

        ["mainIndustries","Siniat", "#B3007E", 0],
        ["mainIndustries","Placo", "#0056A6", 1],
        ["mainIndustries","Knauf", "#67D0FF", 2],
        ["mainIndustries","Challengers", "#888888", 3],

        ["industryTarget","Siniat", "#B3007E", 1],
        ["industryTarget","Potentiel ciblé", "#CD77E2", 0],
        ["industryTarget","Placo", "#0056A6", 2],
        ["industryTarget","Knauf", "#67D0FF", 3],
        ["industryTarget","Challengers", "#888888", 4],

        ["enduitIndustry","Prégy", "#B3007E", 1],
        ["enduitIndustry","Salsi", "#D00000", 0],
        ["enduitIndustry","Croissance", "#DEDEDE", 2],
        ["enduitIndustry","Conquête", "#466A50", 3],

        ["enduitIndustryTarget","Prégy", "#B3007E", 1],
        ["enduitIndustryTarget","Salsi", "#D00000", 0],
        ["enduitIndustryTarget","Cible Croissance", "#CD77E2", 4],
        ["enduitIndustryTarget","Cible Conquête", "#5BB273", 5],
        ["enduitIndustryTarget","Croissance", "#DEDEDE", 2],
        ["enduitIndustryTarget","Conquête", "#466A50", 3],

        ["segmentDnEnduit","P2CD + Enduit", "#B3007E", 1],
        ["segmentDnEnduit","Enduit hors P2CD", "#AC0000", 2],
        ["segmentDnEnduit","Pur prospect", "#8B8B8B", 3],
        ["segmentDnEnduit","Non documenté", "#DEDEDE", 0],

        ["segmentDnEnduitTarget","P2CD + Enduit", "#B3007E", 1],
        ["segmentDnEnduitTarget","Enduit hors P2CD", "#AC0000", 3],
        ["segmentDnEnduitTarget","Cible P2CD", "#D00000", 2],
        ["segmentDnEnduitTarget","Cible Pur Prospect", "#6F6F6F", 4],
        ["segmentDnEnduitTarget","Pur prospect", "#8B8B8B", 5],
        ["segmentDnEnduitTarget","Non documenté", "#DEDEDE", 0],

        ["segmentDnEnduitTargetVisits","P2CD + Enduit", "#B3007E", 2],
        ["segmentDnEnduitTargetVisits","Cible P2CD + Enduit", "#CD77E2", 1],
        ["segmentDnEnduitTargetVisits","Enduit hors P2CD", "#AC0000", 4],
        ["segmentDnEnduitTargetVisits","Cible Enduit hors P2CD", "#D00000", 3],
        ["segmentDnEnduitTargetVisits","Pur prospect", "#8B8B8B", 5],
        ["segmentDnEnduitTargetVisits","Cible Pur Prospect", "#6F6F6F", 6],
        ["segmentDnEnduitTargetVisits","Non documenté", "#DEDEDE", 0],

        ["clientProspect","Client", "#B3007E", 1],
        ["clientProspect","Prospect", "#888888", 2],
        ["clientProspect","Non documenté", "#DEDEDE", 0],

        ["clientProspectTarget","Client", "#B3007E", 2],
        ["clientProspectTarget","Potentiel ciblé", "#CD77E2", 0],
        ["clientProspectTarget","Prospect", "#888888", 3],
        ["clientProspectTarget","Non documenté", "#DEDEDE", 1],

        ["suiviAD","Non renseignées", "#D00000", 2],
        ["suiviAD","Non mises à jour", "#FFE200", 1],
        ["suiviAD","Terminées", "#4AA763", 0],

        ["histoCurve","Nombre de PdV complétés", "#363565", 0],
        ["histoCurve","Cumul en pourcentage", "#F06D0C", 1],

        ["weeks","avant", "#363565", 0],
        ["weeks","s-6", "#363565", 1],
        ["weeks","s-5", "#363565", 2],
        ["weeks","s-4", "#363565", 3],
        ["weeks","s-3", "#363565", 4],
        ["weeks","s-2", "#363565", 5],
        ["weeks","s-1", "#363565", 6],
        ["weeks","s-0", "#363565", 7],

        ["avancementAD", "", "", 0],
        ["visits", "", "", 0],
        ["targetedVisits", "", "", 0],

        ["histoCurve", "Nombre de PdV complétés", "", 0],
        ["histoCurve", "Cumul en pourcentage", "", 1],

        ["pointFeuFilter", "Non point Feu", "", 0],
        ["pointFeuFilter", "Point feu'", "", 1],

        ["visitedFilter", "Visité", "", 0],
        ["visitedFilter", "Non visité", "", 1],

        ["ciblage", "Non ciblé", "", 0],
        ["ciblage", "Ciblé", "", 1],

        ["industriel", "Siniat", "", 0],
        ["industriel", "Placo", "", 1],
        ["industriel", "Knauf", "", 2],
        ["industriel", "Autres", "", 3],

        ["segmentMarketingFilter", "Purs Spécialistes", "", 0],
        ["segmentMarketingFilter", "Multi Spécialistes", "", 1],
        ["segmentMarketingFilter", "Généralistes", "", 2],
        ["segmentMarketingFilter", "Non documenté", "", 3],

      ]
      for list in data:
        label = LabelForGraph.objects.create(axisType=list[0], label=list[1], color=list[2], orderForCompute=list[3])
        cls.__colors[f"{list[0]}:{list[1]}"] = label

      cls.__axis = {}
      listTypeAxis = set(listColor[0] for listColor in data)
      for typeAxis in listTypeAxis:
        listLabel = LabelForGraph.objects.filter(axisType = typeAxis)
        axis = AxisForGraph.objects.create(name=typeAxis)
        for label in listLabel:
          axis.labels.add(label)
        cls.__axis[typeAxis] = axis


  @classmethod
  def create(cls, name, geoOrTrade):
    dictParam = {
      "geo":{
      "Marché P2CD":[
        ["segmentMarketing", "segmentCommercial", "p2cd", AxisForGraph.objects.get(name="segment").id, ["@other"], "no", "Volumétrie par segment", "@sum"],
        ["segmentMarketing", "segmentCommercial", "dn", AxisForGraph.objects.get(name="segment").id, ["@other"], "no", "Nombre de points de vente par segment", "@sum", "b", "PdV", "donut"],
        ["enseigne", "mainIndustries", "p2cd", [], AxisForGraph.objects.get(name="mainIndustries").id, "no", "Volumétrie par enseigne", "Tous segments", "c", "km²", "histoRow"]
      ], "Marché Enduit":[
        ["enduitIndustry", "segmentCommercial", "enduit", AxisForGraph.objects.get(name="enduitIndustry").id, ["@other"], "no", "Volumétrie", "@sum", "a", "T"],
        ["segmentDnEnduit", "segmentCommercial", "dn", AxisForGraph.objects.get(name="segmentDnEnduit").id, ["@other"], "no", "Nombre de points de vente", "@sum", "b", "PdV", "donut"],
        ["enseigne", "enduitIndustry", "enduit", [], AxisForGraph.objects.get(name="enduitIndustry").id, "no", "Volumétrie par enseigne", "Tous segments", "c", "T", "histoRow"]
      ], "PdM P2CD":[
        ["mainIndustries", "segmentMarketing", "p2cd", AxisForGraph.objects.get(name="mainIndustries").id, ["@other"], "classic", "Parts de marché par industrie", "", "a", "%"],
        ["mainIndustries", "segmentMarketing", "p2cd", AxisForGraph.objects.get(name="mainIndustries").id, [], "cols", "Parts de marché par segment", "", "b", "%", "histoColumn"],
        ["enseigne", "mainIndustries", "p2cd", [], AxisForGraph.objects.get(name="mainIndustries").id, "classic", "Parts de marché par enseigne", "Tous segments", "c", "%", "histoRow"]
      ], "PdM Enduit":[
        ["enduitIndustry", "segmentCommercial", "Enduit", AxisForGraph.objects.get(name="enduitIndustry").id, ["@other"], "classic", "Parts de marché par industrie", "", "a", "%"],
        ["enduitIndustry", "segmentMarketing", "Enduit", AxisForGraph.objects.get(name="enduitIndustry").id, [], "cols", "Parts de marché par segment", "", "b", "%", "histoColumn"],
        ["enseigne", "enduitIndustry", "Enduit", [], AxisForGraph.objects.get(name="enduitIndustry").id, "classic", "Parts de marché par enseigne", "Tous segments", "c", "%", "histoRow"]
      ], "PdM P2CD Simulation":[
        ["industryTarget", "segmentMarketing", "p2cd", AxisForGraph.objects.get(name="industryTarget").id, ["@other"], "classic", "Parts de marché par industrie", "", "a", "%", "pieTarget"],
        ["industryTarget", "segmentMarketing", "p2cd", AxisForGraph.objects.get(name="industryTarget").id, [], "cols", "Parts de marché par segment", "", "b", "%", "histoColumn"],
        ["enseigne", "industryTarget", "p2cd", [], AxisForGraph.objects.get(name="industryTarget").id, "classic", "Parts de marché par enseigne", "Tous segments", "c", "%", "histoRow"]
      ], "PdM Enduit Simulation":[
        ["enduitIndustryTarget", "segmentCommercial", "Enduit", AxisForGraph.objects.get(name="enduitIndustryTarget").id, ["@other"], "classic", "Parts de marché par industrie", "", "a", "%", "pieTarget"],
        ["enduitIndustryTarget", "segmentMarketing", "Enduit", AxisForGraph.objects.get(name="enduitIndustryTarget").id, [], "cols", "Parts de marché par segment", "", "b", "%", "histoColumn"],
        ["enseigne", "enduitIndustryTarget", "Enduit", [], AxisForGraph.objects.get(name="enduitIndustryTarget").id, "classic", "Parts de marché par enseigne", "Tous segments", "c", "%", "histoRow"]
      ], "DN P2CD":[
        ["clientProspect", "segmentMarketing", "dn", AxisForGraph.objects.get(name="clientProspect").id, ["@other"], "no", "DN totale", "@sum", "a", "PdV", "donut"],
        ["clientProspect", "segmentMarketing", "dn", AxisForGraph.objects.get(name="clientProspect").id, [], "no", "DN par segment", "", "b", "PdV", "histoColumn"],
        ["enseigne", "clientProspect", "dn", [], AxisForGraph.objects.get(name="clientProspect").id, "no", "DN par enseigne", "Tous segments", "c", "PdV", "histoRow"]
      ], "DN Enduit":[
        ["segmentDnEnduit", "segmentCommercial", "dn", AxisForGraph.objects.get(name="segmentDnEnduit").id, ["@other"], "no", "DN totale", "@sum", "a", "PdV", "donut"],
        ["segmentDnEnduit", "segmentMarketing", "dn", AxisForGraph.objects.get(name="segmentDnEnduit").id, [], "no", "DN par segment", "", "b", "PdV", "histoColumn"],
        ["enseigne", "segmentDnEnduit", "dn", [], AxisForGraph.objects.get(name="segmentDnEnduit").id, "no", "DN par enseigne", "Tous segments", "c", "PdV", "histoRow"]
      ], "DN P2CD Simulation":[
        ["clientProspectTarget", "segmentCommercial", "dn", AxisForGraph.objects.get(name="clientProspectTarget").id, ["@other"], "no", "DN totale", "@sum", "a", "PdV", "pieTarget"],
        ["clientProspectTarget", "segmentMarketing", "dn", AxisForGraph.objects.get(name="clientProspectTarget").id, [], "no", "DN par Segment", "", "b", "PdV", "histoColumn"],
        ["enseigne", "clientProspectTarget", "dn", [], AxisForGraph.objects.get(name="clientProspectTarget").id, "no", "DN par enseigne", "Tous segments", "c", "PdV", "histoRow"]
      ], "Points de Vente P2CD":[
        ["pdvs", "colTableP2cd", "p2cd", [], [], "no", "@titleTableP2cd", "", "a", "m²", "table"]
      ], "Points de Vente Enduit":[
        ["pdvs", "colTableEnduit", "enduit", [], [], "no", "@titleTableEnduit", "", "a", "T", "table"]
      ], "Synthèse P2CD":[
        ["mainIndustries", "lg-1", "P2CD", AxisForGraph.objects.get(name="mainIndustries").id, [], "no", "Volumétrie par division géographique", "", "a", "km²", "histoColumn"],
        ["mainIndustries", "lg-1", "P2CD", AxisForGraph.objects.get(name="mainIndustries").id, [], "cols", "Parts de marché par division géographique", "", "b", "%", "histoColumn"],
        ["clientProspect", "lg-1", "dn", AxisForGraph.objects.get(name="clientProspect").id, [], "no", "DN par division géographique", "", "c", "PdV", "histoColumn"]
      ], "Synthèse Enduit":[
        ["enduitIndustry", "agentFinitions", "enduit", AxisForGraph.objects.get(name="enduitIndustry").id, [], "no", "Volumétrie par division géographique", "", "a", "T", "histoColumn"],
        ["enduitIndustry", "agentFinitions", "enduit", AxisForGraph.objects.get(name="enduitIndustry").id, [], "cols", "Parts de marché par division géographique", "", "b", "%", "histoColumn"],
        ["segmentDnEnduit", "agentFinitions", "dn", AxisForGraph.objects.get(name="segmentDnEnduit").id, [], "no", "DN par division géographique", "", "c", "PdV", "histoColumn"]
      ], "Synthèse P2CD Simulation":[
        ["industryTarget", "lg-1", "P2CD", AxisForGraph.objects.get(name="industryTarget").id, [], "no", "Volumétrie par division géographique", "", "a", "km²", "histoColumnTarget"],
        ["industryTarget", "lg-1", "P2CD", AxisForGraph.objects.get(name="industryTarget").id, [], "cols", "Parts de marché par division géographique", "", "b", "%", "histoColumn"],
        ["clientProspectTarget", "lg-1", "dn", AxisForGraph.objects.get(name="clientProspectTarget").id, [], "no", "DN par division géographique", "", "c", "PdV", "histoColumnTarget"]
      ], "Synthèse Enduit Simulation":[
        ["enduitIndustryTarget", "agentFinitions", "enduit", AxisForGraph.objects.get(name="enduitIndustryTarget").id, [], "no", "Volumétrie par division géographique", "", "a", "T", "histoColumnTarget"],
        ["enduitIndustryTarget", "agentFinitions", "enduit", AxisForGraph.objects.get(name="enduitIndustryTarget").id, [], "cols", "Parts de marché par division géographique", "", "b", "%", "histoColumn"],
        ["segmentDnEnduitTarget", "agentFinitions", "dn", AxisForGraph.objects.get(name="segmentDnEnduitTarget").id, [], "no", "DN par division géographique", "", "c", "PdV", "histoColumn"]
      ], "Suivi AD":[
        ["avancementAD", "avancementAD", "avancementAD", AxisForGraph.objects.get(name="avancementAD").id, ["@other"], "no", "Avancement de l'AD", "", "a", "", "gauge"],
        ["histoCurve", "weeks", "dn", AxisForGraph.objects.get(name="histoCurve").id, [], "no", "Évolution de l'AD au cours des dernières semaines", "", "b", "%|PdV", "histoCurve"],
        ["suiviAD", "lg-1", "dn", AxisForGraph.objects.get(name="suiviAD").id, [], "cols", "Avancement de l'AD par division géographique", "", "c", "%", "histoColumn"]
      ], 'Suivi des Visites':[
        ["visits", "visits", "visits", AxisForGraph.objects.get(name="visits").id, ["@other"], "no", "Avancée des visites", "", "a", "", "gauge"],
        ["targetedVisits", "targetedVisits", "targetedVisits", AxisForGraph.objects.get(name="targetedVisits").id, ["@other"], "no", "Proportion de visites ciblées", "", "b", "", "gauge"],
        ['segmentDnEnduitTargetVisits', "segmentMarketing", "enduit", AxisForGraph.objects.get(name="segmentDnEnduitTargetVisits").id, ["@other"], "no", "Répartition des visites en volume", "@sum", "c", "T"],
        ['segmentDnEnduitTargetVisits', "segmentMarketing", "visits", AxisForGraph.objects.get(name="segmentDnEnduitTargetVisits").id, ["@other"], "no", "Répartition des visites en DN", "@sum", "d", "visites"]
      ]
      }, "trade":{
      "Marché P2CD":[
        ["segmentMarketing", "segmentCommercial", "p2cd", AxisForGraph.objects.get(name="segment").id, ["@other"], "no", "Volumétrie par segment", "@sum"],
        ["segmentMarketing", "segmentCommercial", "dn", AxisForGraph.objects.get(name="segment").id, ["@other"], "no", "Nombre de points de vente par segment", "@sum", "b", "PdV", "donut"],
        ["lt-1", "mainIndustries", "p2cd", [], AxisForGraph.objects.get(name="mainIndustries").id, "no", "Volumétrie par enseigne", "Tous segments", "c", "km²", "histoRow"]
      ], "Marché Enduit":[
        ["enduitIndustry", "segmentCommercial", "enduit", AxisForGraph.objects.get(name="enduitIndustry").id, ["@other"], "no", "Volumétrie", "@sum", "a", "T"],
        ["segmentDnEnduit", "segmentCommercial", "dn", AxisForGraph.objects.get(name="segmentDnEnduit").id, ["@other"], "no", "Nombre de points de vente", "@sum", "b", "PdV", "donut"],
        ["lt-1", "enduitIndustry", "enduit", [], AxisForGraph.objects.get(name="enduitIndustry").id, "no", "Volumétrie par enseigne", "Tous segments", "c", "T", "histoRow"]
      ], "PdM P2CD":[
        ["mainIndustries", "segmentMarketing", "p2cd", AxisForGraph.objects.get(name="mainIndustries").id, ["@other"], "classic", "Parts de marché par industrie", "", "a", "%"],
        ["mainIndustries", "segmentMarketing", "p2cd", AxisForGraph.objects.get(name="mainIndustries").id, [], "cols", "Parts de marché par segment", "", "b", "%", "histoColumn"],
        ["lt-1", "mainIndustries", "p2cd", [], AxisForGraph.objects.get(name="mainIndustries").id, "classic", "Parts de marché par enseigne", "Tous segments", "c", "%", "histoRow"]
      ], "PdM Enduit":[
        ["enduitIndustry", "segmentCommercial", "Enduit", AxisForGraph.objects.get(name="enduitIndustry").id, ["@other"], "classic", "Parts de marché par industrie", "", "a", "%"],
        ["enduitIndustry", "segmentMarketing", "Enduit", AxisForGraph.objects.get(name="enduitIndustry").id, [], "cols", "Parts de marché par segment", "", "b", "%", "histoColumn"],
        ["lt-1", "enduitIndustry", "Enduit", [], AxisForGraph.objects.get(name="enduitIndustry").id, "classic", "Parts de marché par enseigne", "Tous segments", "c", "%", "histoRow"]
      ],"DN P2CD":[
        ["clientProspect", "segmentMarketing", "dn", AxisForGraph.objects.get(name="clientProspect").id, ["@other"], "no", "DN totale", "@sum", "a", "PdV", "donut"],
        ["clientProspect", "segmentMarketing", "dn", AxisForGraph.objects.get(name="clientProspect").id, [], "no", "DN par segment", "", "b", "PdV", "histoColumn"],
        ["lt-1", "clientProspect", "dn", [], AxisForGraph.objects.get(name="clientProspect").id, "no", "DN par enseigne", "Tous segments", "c", "PdV", "histoRow"]
      ], "DN Enduit":[
        ["segmentDnEnduit", "segmentCommercial", "dn", AxisForGraph.objects.get(name="segmentDnEnduit").id, ["@other"], "no", "DN totale", "@sum", "a", "PdV", "donut"],
        ["segmentDnEnduit", "segmentMarketing", "dn", AxisForGraph.objects.get(name="segmentDnEnduit").id, [], "no", "DN par segment", "", "b", "PdV", "histoColumn"],
        ["lt-1", "segmentDnEnduit", "dn", [], AxisForGraph.objects.get(name="segmentDnEnduit").id, "no", "DN par enseigne", "Tous segments", "c", "PdV", "histoRow"]
      ],"Points de Vente P2CD":[
        ["pdvs", "colTableP2cd", "p2cd", [], [], "no", "@titleTableP2cd", "", "a", "m²", "table"]
      ], "Points de Vente Enduit":[
        ["pdvs", "colTableEnduit", "enduit", [], [], "no", "@titleTableEnduit", "", "a", "T", "table"]
      ], "Synthèse P2CD":[
        ["mainIndustries", "lgp-1", "P2CD", AxisForGraph.objects.get(name="mainIndustries").id, [], "no", "Volumétrie par division géographique", "", "a", "km²", "histoColumn"],
        ["mainIndustries", "lgp-1", "P2CD", AxisForGraph.objects.get(name="mainIndustries").id, [], "cols", "Parts de marché par division géographique", "", "b", "%", "histoColumn"],
        ["clientProspect", "lgp-1", "dn", AxisForGraph.objects.get(name="clientProspect").id, [], "no", "DN par division géographique", "", "c", "PdV", "histoColumn"]
      ], "Synthèse Enduit":[
        ["enduitIndustry", "agentFinitions", "enduit", AxisForGraph.objects.get(name="enduitIndustry").id, [], "no", "Volumétrie par division géographique", "", "a", "T", "histoColumn"],
        ["enduitIndustry", "agentFinitions", "enduit", AxisForGraph.objects.get(name="enduitIndustry").id, [], "cols", "Parts de marché par division géographique", "", "b", "%", "histoColumn"],
        ["segmentDnEnduit", "agentFinitions", "dn", AxisForGraph.objects.get(name="segmentDnEnduit").id, [], "no", "DN par division géographique", "", "c", "PdV", "histoColumn"]
      ], 
      'other':[
        ["segmentMarketing", "segmentCommercial", "p2cd", [], ["@other"], "no", "Vente en volume"],
        ["segmentMarketing", "segmentCommercial", "dn", [], ["@other"], "no", "Nombre de PdV", "", "b"],
        ["enseigne", "mainIndustries", "p2cd", [], ["Siniat", "Placo", "Knauf", "Challengers"], "no", "Volume par enseigne", "", "c", "histoRow"],
        ["enseigne", "mainIndustries", "dn", [], ["Siniat", "Placo", "Knauf", "Challengers"], "no", "Volume par industrie", "Tous segments", "c", "histoColumn"]
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
