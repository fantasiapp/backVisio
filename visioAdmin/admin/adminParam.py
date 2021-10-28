from visioServer.models import ParamVisio, Sales, Pdv
from visioServer.modelStructure.dataDashboard import DataDashboard, Sales, Industry, Product, Target
from django.db import models
from datetime import datetime


class AdminParam:
  fieldNamePdv = {
      "code":"PDV code", "name":"PDV", "drv":"Drv", "agent":"Agent", "agentFinitions":"Agent Finition", "dep":"Département", "bassin":"Bassin", "ville":"Ville", "latitude":"Latitude",
      "longitude":"Longitude", "segmentCommercial":"Segment Commercial", "segmentMarketing":"Segment Marketing", "enseigne":"Enseigne",
      "ensemble":"Ensemble", "sousEnsemble":"Sous-Ensemble", "site":"Site", "pointFeu":"Point Feu", "closedAt":"Fermé le"}
  fieldNameSales = {
    "code":"PDV code", "name":"PDV", "drv":"Drv", "agent":"Agent", "dep":"Département", "sale":"vend des plaques", "redistributed":"Non Redistribué",
    "redistributedFinitions":"Non Redistribué enduit", "onlySiniat":"Seulement Siniat", "closedAt":"Fermé le"}

  def __init__(self, dataDashboard):
    self.dataDashboard = dataDashboard

  def openAd(self):
    isAdOpen = ParamVisio.dictValues()["isAdOpen"]
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
    after = "Fermée" if isAdOpen else "Ouverte"
    return {"message":f"L'AD était {before}, elle est maintenant {after}"}

  def visualizePdv(self):
    pdvs = getattr(self.dataDashboard, "__pdvs")
    indexes = Pdv.listIndexes()
    listFields = Pdv.listFields()
    pdvsToExport = [self.__editPdv(line, listFields, indexes, self.fieldNamePdv) for line in pdvs.values()]
    return {'titles':list(self.fieldNamePdv.values()), 'values':pdvsToExport}

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
    dictId = {"Siniat":Industry.objects.get(name="Siniat").id, "Prégy":Industry.objects.get(name="Prégy").id, "Salsi":Industry.objects.get(name="Salsi").id,
    "Plaque":Product.objects.get(name="plaque").id,  "Cloison":Product.objects.get(name="cloison").id, "Doublage":Product.objects.get(name="doublage").id, "Enduit":Product.objects.get(name="enduit").id}
    print(dictId, Sales.listFields())
    salesToExport = [self.__editSales(line, listFields, indexes, self.fieldNameSales, dictId, Sales.listFields()) for line in pdvs.values()]
    return {'titles':list(self.fieldNameSales.values()) + ["Plaque", "Cloison", "Doublage", "Prégy", "Salsi"], 'values':salesToExport}

  def __editSales(self, line, listFields, indexes, fieldNameSales, dictId, fieldSales):
    pdvLine = self.__editPdv(line, listFields, indexes, fieldNameSales)
    indexSale = listFields.index("sales")
    saleLine = [0, 0, 0, 0, 0]
    for sale in line[indexSale]:
      if sale[fieldSales.index("industry")] == dictId["Siniat"]:
        if sale[fieldSales.index("product")] == dictId["Plaque"]:
          saleLine[0] = '{:,}'.format(sale[fieldSales.index("volume")]).replace(',', ' ')
        if sale[fieldSales.index("product")] == dictId["Cloison"]:
          saleLine[1] = '{:,}'.format(sale[fieldSales.index("volume")]).replace(',', ' ')
        if sale[fieldSales.index("product")] == dictId["Doublage"]:
          saleLine[2] = '{:,}'.format(sale[fieldSales.index("volume")]).replace(',', ' ')
      if sale[fieldSales.index("industry")] == dictId["Prégy"] and sale[fieldSales.index("product")] == dictId["Enduit"]:
        saleLine[3] = '{:,}'.format(sale[fieldSales.index("volume")]).replace(',', ' ')
      if sale[fieldSales.index("industry")] == dictId["Salsi"] and sale[fieldSales.index("product")] == dictId["Enduit"]:
        saleLine[4] = '{:,}'.format(sale[fieldSales.index("volume")]).replace(',', ' ')
    return pdvLine + saleLine

  def visualizeTarget(self):
    indexTarget = Pdv.listFields().index("target")
    targets = [self.__editTarget(id, line, line[indexTarget], Pdv.listFields(), Target.listFields()) for id, line in getattr(self.dataDashboard, "__pdvs").items()]
    targets = [target for target in targets if target]
    print(targets[0])
    print(Target.listFields())
    return {'titles':["Test", "PDV code", "Pdv", "Date d'envoi", "Redistribué", "Redistribué enduit", "Ne vend pas de plaque", "Ciblé enduit", "Ciblage P2CD", "Feu ciblage", "Bassin", "Commentaires"], 'values':targets}

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
      if pdv[0] == '684695':
        print(target)
      return [f'<button id="Pdv:{idPdv}" class="buttonTarget">OK</button>'] + pdv + targetFormated
    return False