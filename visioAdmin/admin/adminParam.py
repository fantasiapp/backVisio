from visioServer.models import ParamVisio, Sales, Pdv, Industry, Product, Target, DataAdmin
from visioServer.modelStructure.dataDashboard import DataDashboard
# from django.db import models
from datetime import datetime
# from dotenv import load_dotenv
import json
import os
from visioAdmin.dataModel.readXlsx import ReadXlsxRef


class AdminParam:
  fieldNamePdv = False
  fieldNameSales = False

  def __init__(self, dataDashboard):
    self.dataDashboard = dataDashboard
    if not AdminParam.fieldNamePdv:
      AdminParam.fieldNamePdv  = json.loads(os.getenv('FIELD_PDV_BASE_PRETTY'))
      AdminParam.fieldNameSales  = json.loads(os.getenv('FIELD_PDV_SALE_BASE_PRETTY'))
      AdminParam.titleTarget = json.loads(os.getenv('TITLE_TARGET'))
      AdminParam.dataSales = json.loads(os.getenv('DATA_SALES'))

  def switchAdStatus(self):
    isAdOpen = ParamVisio.getValue("isAdOpen")
    before = "Ouverte" if isAdOpen else "Fermée"
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

  def visualizePdvCurrent(self):
    pdvs = getattr(self.dataDashboard, "__pdvs")
    indexes = Pdv.listIndexes()
    listFields = Pdv.listFields()
    pdvsToExport = [self.__editPdv(line, listFields, indexes, self.fieldNamePdv) for line in pdvs.values()]
    return {'titles':list(self.fieldNamePdv.values()), 'values':pdvsToExport}

  def visualizePdvSaved(self):
    fileName = DataAdmin.getLastSavedObject().fileNameRef
    readXlsRef = ReadXlsxRef(fileName, self.dataDashboard)
    if not readXlsRef.errors:
      return readXlsRef.json
    return {"titles":["A", "B"], "values":[["1", "2"], ["3", "4"]]}

  def __editPdv(self, line, listFields, indexes, fieldNamePdv):
    lineFormated = []
    for index in range(len(line)):
      if listFields[index] in fieldNamePdv:
        if index in indexes:
          dictData = getattr(DataDashboard, f"__{listFields[index]}", False)
          if dictData:
            value = dictData[line[index]]
            if isinstance(value, list):
              value = value[0]
            lineFormated.append(value)
        elif isinstance(line[index], bool):
          lineFormated.append("Oui" if line[index] else "Non")
        elif listFields[index] == "closedAt":
            lineFormated.append(line[index][:10] if line[index] else '')
        else:
          lineFormated.append(line[index])
    return lineFormated

  def visualizeSales(self):
    pdvs = getattr(self.dataDashboard, "__pdvs")
    indexes = Pdv.listIndexes()
    listFields = Pdv.listFields()
    dictId = {field:(Industry if val == "ind" else Product).objects.get(name=field).id for field, val in self.dataSales.items()}
    salesToExport = [self.__editSales(line, listFields, indexes, self.fieldNameSales, dictId, Sales.listFields()) for line in pdvs.values()]
    return {'titles':list(self.fieldNameSales.values()) + ["Plaque", "Cloison", "Doublage", "Prégy", "Salsi"], 'values':salesToExport}

  def __editSales(self, line, listFields, indexes, fieldNameSales, dictId, fieldSales):
    pdvLine = self.__editPdv(line, listFields, indexes, fieldNameSales)
    indexSale = listFields.index("sales")
    saleLine = [0, 0, 0, 0, 0]
    for sale in line[indexSale]:
      if sale[fieldSales.index("industry")] == dictId["Siniat"]:
        if sale[fieldSales.index("product")] == dictId["Plaque"]:
          saleLine[0] = '{:,}'.format(int(sale[fieldSales.index("volume")])).replace(',', ' ')
        if sale[fieldSales.index("product")] == dictId["Cloison"]:
          saleLine[1] = '{:,}'.format(int(sale[fieldSales.index("volume")])).replace(',', ' ')
        if sale[fieldSales.index("product")] == dictId["Doublage"]:
          saleLine[2] = '{:,}'.format(int(sale[fieldSales.index("volume")])).replace(',', ' ')
      if sale[fieldSales.index("industry")] == dictId["Prégy"] and sale[fieldSales.index("product")] == dictId["Enduit"]:
        saleLine[3] = '{:,}'.format(int(sale[fieldSales.index("volume")])).replace(',', ' ')
      if sale[fieldSales.index("industry")] == dictId["Salsi"] and sale[fieldSales.index("product")] == dictId["Enduit"]:
        saleLine[4] = '{:,}'.format(int(sale[fieldSales.index("volume")])).replace(',', ' ')
    return pdvLine + saleLine

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