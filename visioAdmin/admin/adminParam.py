from visioServer.models import *
# from visioServer.modelStructure.dataDashboard import DataDashboard
from datetime import datetime
# from dotenv import load_dotenv
import json
import os
# from visioAdmin.dataModel.readXlsx import ReadXlsxRef

class AdminParam:
  fieldNamePdv = False
  fieldNameSales = False

  def __init__(self, dataDashboard):
    self.dataDashboard = dataDashboard
    if not AdminParam.fieldNamePdv:
      AdminParam.titleTarget = json.loads(os.getenv('TITLE_TARGET'))

  def paramSynonymsInit(self):
    return Synonyms.getDictValues()

  def fillupSynonym(self, dictSynonymJson):
    inversePretty = {value:key for key, value in Synonyms.prettyPrint.items()}
    dictSynonym = json.loads(dictSynonymJson)
    for field, dictValue in dictSynonym.items():
      field = inversePretty[field]
      for originalName, value in dictValue.items():
        Synonyms.setValue(field, originalName, value)
    return {"fillupSynonym":"Les valeurs ont bien été enregistrées"}


  def switchAdStatus(self):
    isAdOpen = ParamVisio.getValue("isAdOpen")
    ParamVisio.setValue("isAdOpen", False if isAdOpen else True)
    if ParamVisio.getValue("isAdOpen"):
      pdvs = getattr(self.dataDashboard, "__pdvs")
      indexSales = Pdv.listFields().index("sales")
      indexDate = Sales.listFields().index("date")
      listSales = [pdv[indexSales] for pdv in pdvs.values()]
      for sales in listSales:
        for sale in sales:
          sale[indexDate] = None
      for sale in Sales.objects.filter(date__isnull=False):
        sale.date = None
        sale.save()
    return {"isAdOpen":ParamVisio.getValue("isAdOpen")}

  def visualizeTarget(self):
    indexTarget = Pdv.listFields().index("target")
    targets = [self.__editTarget(id, line, line[indexTarget], Pdv.listFields(), Target.listFields()) for id, line in getattr(self.dataDashboard, "__pdvs").items()]
    targets = [target for target in targets if target]
    return {'titles':AdminParam.titleTarget, 'values':targets}

  def __editTarget(self, idPdv, line, target, fieldsPdv, fieldsTarget):
    if target:
      pdv = [line[fieldsPdv.index(field)] for  field in ["code", "name"]]
      targetFormated = [datetime.fromtimestamp(target[fieldsTarget.index("date")]).strftime('%Y-%m-%d')]
      fieldsBool = ['redistributed', 'redistributedFinitions', 'sale']
      targetFormated += ["Non" if target[fieldsTarget.index(field)] else "Oui" for field in fieldsBool]
      targetFormated += ["Oui" if target[fieldsTarget.index("targetFinitions")] else "Non"]
      targetFormated.append('{:,}'.format(target[fieldsTarget.index("targetP2CD")]).replace(',', ' '))
      greenLight = {"g":"Vert", "o":"Orange", "r":"Rouge"}
      targetFormated.append(greenLight[target[fieldsTarget.index("greenLight")]] if target[fieldsTarget.index("greenLight")] else "Aucun")
      targetFormated += [target[fieldsTarget.index(field)] for field in ["bassin", "commentTargetP2CD"]]
      return [f'<button id="Pdv:{idPdv}" class="buttonTarget">OK</button>'] + pdv + targetFormated
    return False