from visioServer.models import WidgetCompute, WidgetParams, Widget
import json

class CreateWidgetParam:
  __dictWidget = {}

  @classmethod
  def initialize(cls):
    if not cls.__dictWidget:
      for name in ["pie", "donut", "image", "histoRow", "histoColumn", "table"]:
        cls.__dictWidget[name] = Widget.objects.create(name=name)

  @classmethod
  def create(cls, name):
    dictParam = {
      "Marché P2CD":[
        ["segmentMarketing", "segmentCommercial", "p2cd", [], ["@other"], False, "Vente en volume"],
        ["segmentMarketing", "segmentCommercial", "dn", [], ["@other"], False, "Nombre de Pdv", "", "b"],
        ["enseigne", "industrie", "p2cd", [], ["Siniat", "Placo", "Knauf", "@other"], False, "Volume par enseigne", "", "c", "histoRow"]
      ], "Marché Enduit":[
        ["segmentMarketing", "segmentCommercial", "p2cd", [], ["@other"], False, "Volume Total"],
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
    widgetCompute = WidgetCompute.objects.create(axis1=axis1, axis2=axis2, indicator=ind, groupAxis1=json.dumps(grAx1), groupAxis2=json.dumps(grAx2), percent=percent)
    return WidgetParams.objects.create(title=title, subTitle=subTitle, position=pos, widget=cls.__dictWidget[widget], widgetCompute=widgetCompute)