from django.core.exceptions import ObjectDoesNotExist
from django.db.models import fields
from visioAdmin.admin.adminParam import AdminParam
from visioServer.models import *
from visioServer.modelStructure.dataDashboard import DataDashboard
import json
import os
from openpyxl import load_workbook
from pathlib import Path
from django.db import connection

class AdminUpdate:
  fieldNamePdv = False
  __errors = []
  __errorStatus = ""

  def __init__(self, dataDashboard):
    self.dataDashboard = dataDashboard
    AdminUpdate.__errors = []
    AdminUpdate.__errorStatus = ""
    if not AdminUpdate.fieldNamePdv:
      AdminUpdate.fieldNamePdv  = json.loads(os.getenv('FIELD_PDV_BASE_PRETTY'))
      AdminUpdate.fieldNameSales  = json.loads(os.getenv('FIELD_PDV_SALE_BASE_PRETTY'))
      AdminUpdate.titleTarget = json.loads(os.getenv('TITLE_TARGET'))
      AdminUpdate.dataSales = json.loads(os.getenv('DATA_SALES'))
      AdminUpdate.fieldXlsxRef = json.loads(os.getenv('DICO_FIELD_XLSX_REF'))
      AdminUpdate.fieldXlsxVol = json.loads(os.getenv('DICO_FIELD_XLSX_VOL'))
      AdminUpdate.fieldXlsxDbRef = json.loads(os.getenv('FIELD_PDV_XLSX_BASE'))
      AdminUpdate.pathRef = os.getenv('PATH_FILE_REF')
      AdminUpdate.pathVol = os.getenv('PATH_FILE_VOL')
      AdminUpdate.sheetNameRef = os.getenv('SHEET_NAME_REF')
      AdminUpdate.sheetNameVol = json.loads(os.getenv('SHEET_NAME_VOL'))
      AdminUpdate.keyFieldRef = os.getenv('KEY_FIELD_REF')
      AdminUpdate.keyFieldVol = os.getenv('KEY_FIELD_VOL')

      AdminUpdate.xlsxData = None
      AdminUpdate.creationElement = None
      AdminUpdate.replacedAgent = None
      AdminUpdate.response = None

  @property
  def getErrors(self):
    if self.__errors:
      return {"error":True, "title":self.__errorStatus, "content":"\r\n".join(self.__errors)}
    return False

  @classmethod
  def setError(cls, title, content):
    if title == "error":
      cls.__errorStatus = "Erreur"
    elif title == "warning" and cls.__errorStatus != "error":
      cls.__errorStatus = "Attention"
    elif title == "info" and not cls.__errorStatus:
      cls.__errorStatus = "Information"
    cls.__errors.append(content)

  def visualizePdv(self, nature):
    if nature == "both":
      self.__visualizePdvBoth()
    file = "refSave.json" if nature == "saved" else "ref.json"
    if not os.path.isfile(f"./visioAdmin/dataFile/Json/{file}"):
      self.__createSaveJson()
    with open(f"./visioAdmin/dataFile/Json/{file}") as jsonFile:
      pdvsToExport = json.load(jsonFile)
    return {'titles':list(self.fieldNamePdv.values()), 'values':pdvsToExport}


  def __visualizePdvBoth(self):
    data, pdvIdCode, index, fieldsName, pdvsToExport, newPdv = {}, {}, 0, list(self.fieldNamePdv.values()), [], []
    indexCode = fieldsName.index("PDV code")
    for key, file in {"current":"ref.json", "saved":"refSave.json"}.items():
      if not os.path.isfile(f"./visioAdmin/dataFile/Json/{file}"):
        self.__createSaveJson()
      with open(f"./visioAdmin/dataFile/Json/{file}") as jsonFile:
        data[key] = json.load(jsonFile)
    for line in data["current"]:
      pdvIdCode[line[indexCode]] = index 
      index += 1
    for index in range(len(data["saved"])):
      line = data["saved"][index]
      code = line[indexCode]
      indexEquiv = pdvIdCode[code] if code in pdvIdCode else None
      if indexEquiv:
        lineEquiv = data["current"][indexEquiv]
        lineExported = []
        for indexField in range(len(line)):
          if line[indexField] == lineEquiv[indexField]:
            lineExported.append(line[indexField])
          else:
            print(line[indexCode], line[indexField], lineEquiv[indexField])
            lineExported.append(str(line[indexField])+"<br>"+str(lineEquiv[indexField]))
            print(lineExported)
        pdvsToExport.append(lineExported)
      else:
        pdvsToExport.append(line)
        newPdv.append(line[indexCode])
    print("newPdv", newPdv)
    return {'titles':fieldsName, 'values':pdvsToExport, 'new':newPdv}

  def visualizeSalesCurrent(self):
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

  def updateFile (self, fileNature):
    if fileNature == "referentiel":
      return self.__updateFileRef()
    if fileNature == "volume":
      return self.__updateFileVol()

  def __updateFileRef(self):
    dictSheet = self.__updateLoad("referentiel")
    AdminUpdate.xlsxData = dictSheet["Ref"] if dictSheet else False
    if AdminUpdate.xlsxData:
      title = self.__findTitlesRef()
      if not title: return False
      data = self.__findValuesRef(list(title.values()), title[self.keyFieldRef])
      AdminUpdate.xlsxData = self.__buildStructureRef(title, data, getattr(self.dataDashboard, "__structurePdvs"))
      response = self.__saveDataRef()
      if response:
        return response
      else:
        return self.updateRefWithAgent({})
    else:
      return False

  def __updateFileVol(self):
    dictSheet = self.__updateLoad("volume")
    if dictSheet:
      AdminUpdate.xlsxData = dictSheet
      titles = self.__findTitlesVol()
      if not titles: return False
      data = self.__findValuesVol(titles, titles["siniat"][self.keyFieldVol])
      AdminUpdate.xlsxData = {key:{"titles":value, "data":data[key]} for key, value in titles.items()}
      self.__saveDataVol()
    return False

  def __updateLoad(self, fileNature):
    fileName = DataAdmin.getLastSavedObject().fileNameRef if fileNature == "referentiel" else DataAdmin.getLastSavedObject().fileNameVol
    path = self.pathRef if fileNature == "referentiel" else self.pathVol
    pathFile = Path.cwd() / f"{path}{fileName}"
    dictSheet = {}
    if pathFile.exists():
      for key, sheetName in {"Ref":self.sheetNameRef}.items() if fileNature == "referentiel" else self.sheetNameVol.items():
        try:
          xlsxworkbook = load_workbook(pathFile, data_only=True)
          dictSheet[key] = xlsxworkbook[sheetName]
        except:
          self.setError("error", f"L'onglet {sheetName} n'existe pas.")
          return False
      return dictSheet
    self.setError("error", f"Le fichier {fileName} n'est pas un fichier xlsx conforme.")
    return False

  def __findTitlesRef(self):
    column, dictField = 1, {}
    value = AdminUpdate.xlsxData.cell(row=1, column=column).value
    if value == self.keyFieldRef:
      while value:
        if value in self.fieldXlsxRef:
          dictField[value] = column
        column += 1
        value = AdminUpdate.xlsxData.cell(row=1, column=column).value
      for title in self.fieldXlsxRef:
        if not title in dictField:
          self.setError("error", f"Le champ {title} n'est pas présent dans les titres colonnes.")
          return False
      return dictField
    else:
      self.setError("error", f"Le champ {self.keyFieldRef} n'est pas présent en début de fichier.")
      return False

  def __findTitlesVol(self):
    dictField = {}
    for key, sheet in AdminUpdate.xlsxData.items():
      dictField[key]={}
      column = 1
      row = 2 if key == "siniat" else 1
      value = sheet.cell(row=row, column=column).value
      if value == self.keyFieldVol:
        while value:
          if value in self.fieldXlsxVol[key]:
            dictField[key][value] = column
          column += 1
          value = sheet.cell(row=row, column=column).value
        for title in self.fieldXlsxVol[key]:
          if not title in dictField[key]:
            self.setError("error", f"Le champ {title} n'est pas présent dans les titres colonnes pour les valeurs de {key}.")
            return False
      else:
        self.setError("error", f"Le champ {self.keyFieldVol} n'est pas présent dans les titres colonnes.")
        return False
    return dictField
  
  def __findValuesRef(self, titleColumns, codeColumn):
    row, data = 2, []
    while AdminUpdate.xlsxData.cell(row=row, column=codeColumn).value:
      newLine = [AdminUpdate.xlsxData.cell(row=row, column=column).value for column in titleColumns]
      data.append(newLine)
      row += 1
    return data

  def __findValuesVol(self, titleColumns, codeColumn):
    data = {key:[] for key in titleColumns.keys()}
    for key, title in titleColumns.items():
      row = 3 if key == "siniat" else 2
      while AdminUpdate.xlsxData[key].cell(row=row, column=codeColumn).value:
        newLine = [AdminUpdate.xlsxData[key].cell(row=row, column=column).value for column in title.values()]
        data[key].append(newLine)
        row += 1
    return data

  def __buildStructureRef(self, title, data, structurePdvs):
    structure = {"pdvs":{}, "newPdvs":[]}
    listId = self.__buildInverseStructure(structurePdvs)
    for line in data:
      indexData, lineAnalysis = 0, {"missingValues":[]}
      for xlsxTitle in title.keys():
        self.__treatLineField(line[indexData], self.fieldXlsxDbRef[xlsxTitle], lineAnalysis, listId)
        indexData += 1
      id = lineAnalysis["idPdv"]
      del lineAnalysis["idPdv"]
      if id == "new":
        structure["newPdvs"].append(lineAnalysis)
      else:
        self.__checkDiff(lineAnalysis, structurePdvs, getattr(self.dataDashboard, "__pdvs")[id])
        structure["pdvs"][id] = lineAnalysis
    structure["oldPdvs"] = [id for id in getattr(self.dataDashboard, "__pdvs").keys() if not id in structure["pdvs"]]
    return structure

  def __treatLineField(self, value, dbField, lineAnalysis, listId):
    if dbField == "code_old": self.__treatLineCodeOld(value, lineAnalysis, listId)
    elif dbField == "code" and lineAnalysis["code"] != value:
      lineAnalysis["codeNew"] = value
    elif dbField == "pointFeu":
      lineAnalysis[dbField] = True if value == "O" else False
    elif dbField in listId:
      if value in listId[dbField]:
        lineAnalysis[dbField] = listId[dbField][value]
      elif dbField == "segmentMarketing":
        lineAnalysis[dbField] = listId[dbField]["Autres"]
      elif value != None:
        lineAnalysis[dbField] = value
        lineAnalysis["missingValues"].append(dbField)
    else: lineAnalysis[dbField] = value

  def __treatLineCodeOld(self, value, lineAnalysis, listId):
    lineAnalysis["code"] = value
    if str(value) in listId["pdvCode"]:
      lineAnalysis["idPdv"] = listId["pdvCode"][str(value)]
    else:
      lineAnalysis["idPdv"] = "new"

  def __buildInverseStructure (self, structurePdvs):
    listId = {}
    indexCode = structurePdvs.index("code")
    listId["pdvCode"] = {line[indexCode]:id for id, line in getattr(self.dataDashboard, "__pdvs").items()}
    for field in ["ville", "dep", "agent", "drv", "segmentMarketing", "enseigne", "ensemble", "sousEnsemble", "site", "bassin", "segmentCommercial"]:
      dicoField = getattr(self.dataDashboard, f"__{field}")
      if field == "segmentMarketing":
        dicoEquiv = {"Purs Spécialistes":"Pur Spécialiste", "Multi Spécialistes":"Multispécialiste", "Généralistes":"Généraliste"}
        dicoField = {id:dicoEquiv[name] for id, name in dicoField.items() if name in dicoEquiv}
        other = SegmentMarketing.objects.get(name="Autres", currentYear=True)
        dicoField[other.id] = other.name
      elif field == "bassin":
        bassinBase = Bassin.objects.filter(currentYear=True)
        dicoField = {bassin.id:bassin.name for bassin in bassinBase}
      listId[field] = {name:id for id, name in dicoField.items()}
    return listId

  def __checkDiff(self, lineAnalysis, structurePdvs, pdvCurrent):
    unusedFields = lineAnalysis['missingValues'] + ['missingValues', 'code', 'codeNew', 'nbVisits']
    diff = [field for field, value in lineAnalysis.items() if not field in unusedFields and self.__areDifferent(field, value, structurePdvs, pdvCurrent)]
    lineAnalysis["differences"] = diff

  def __areDifferent(self, field, value, structurePdvs, pdvCurrent):
    index = structurePdvs.index(field)
    return abs(value - pdvCurrent[index]) > 0.001 if isinstance(value, float) else value != pdvCurrent[index]

  def __saveDataRef(self):
    self.__agentFinitionsDelete()
    dictClass = {
      "drv":{"current":Drv, "save":DrvSave},
      "ville":{"current":Ville, "save":VilleSave},
      "dep":{"current":Dep, "save":DepSave},
      "segmentMarketing":{"current":SegmentMarketing, "save":SegmentMarketingSave},
      "segmentCommercial":{"current":SegmentCommercial, "save":SegmentCommercialSave},
      "enseigne":{"current":Enseigne, "save":EnseigneSave},
      "ensemble":{"current":Ensemble, "save":EnsembleSave},
      "sousEnsemble":{"current":SousEnsemble, "save":SousEnsembleSave},
      "site":{"current":Site, "save":SiteSave},
      "bassin":{"current":Bassin, "save":BassinSave},
      }
    AdminUpdate.creationElement = self.__saveDataRefFillUpTable(dictClass)
    AdminUpdate.replacedAgent = self.__saveDataRefFillUpAgent()
    if AdminUpdate.replacedAgent:
      listAgent = [{"newName":key, "oldName":value['oldName']} for key, value in AdminUpdate.replacedAgent.items()]
      return {"warningAgent":listAgent}
    else:
      return self.__endTreatment()

  def __saveDataRefFillUpTable(self, dictClass):
    creation = {}
    for table, classes in dictClass.items():
      creation[table] = {}
      setPdv = {line[table] for line in AdminUpdate.xlsxData["pdvs"].values() if not table in line['missingValues'] and table in line}
      setNewPdv = {line[table] for line in AdminUpdate.xlsxData["newPdvs"] if not table in line['missingValues'] and table in line}
      setOldPdv = {getattr(Pdv.objects.get(id=id), table).id for id in AdminUpdate.xlsxData["oldPdvs"]}
      setIdUsed = setPdv | setNewPdv | setOldPdv
      setPdvMissing = {line[table] for line in AdminUpdate.xlsxData["pdvs"].values() if table in line['missingValues'] and table in line}
      setNewPdvMissing = {line[table] for line in AdminUpdate.xlsxData["newPdvs"] if table in line['missingValues'] and table in line}
      setNewValues = setPdvMissing | setNewPdvMissing
      self.__createDefaultValues(classes["save"])
      for id in setIdUsed:
        if not classes["save"].objects.filter(id=id):
          existingObject = classes["current"].objects.get(id=id)
          if not table in ["ville"]:
            classes["save"].objects.create(id=id, name=existingObject.name, idF=existingObject.idF)
          else:
            classes["save"].objects.create(id=id, name=existingObject.name)
      for name in setNewValues:
        exists = classes["save"].objects.filter(name=name)
        if exists:
          creation[table][name] = exists[0].id
        else:
          new = classes["save"].objects.create(name=name)
          if not table in ["ville"]:
            new.idF = new.id
            new.save()
          creation[table][name] = new.id
    return creation

  def __createDefaultValues(self, classesSelected):
    classesSelected.objects.all().delete()
    tableName = classesSelected.objects.model._meta.db_table
    with connection.cursor() as cursor:
      cursor.execute(f"ALTER TABLE {tableName} AUTO_INCREMENT=1;")
    listDefault = {
      "non segmenté":(17, SegmentCommercialSave), 
      "Fermé":(5, SegmentMarketingSave),
      "Not assigned":(1, SiteSave),
      "Not assigned":(1, SousEnsembleSave),
      "Not assigned":(1, EnsembleSave),
      "Non identifié":(18, EnseigneSave),
      }
    for name, (id, classObject) in listDefault.items():
      if classesSelected == classObject:
        classObject.objects.create(id=id, name=name, idF=id)


  def __saveDataRefFillUpAgent(self):
    indexAgent = getattr(self.dataDashboard, "__structurePdvs").index("agent")
    currentPdvs = getattr(self.dataDashboard, "__pdvs")
    currentAgent = getattr(self.dataDashboard, "__agent")
    dataAgent = {id:line['agent'] for id, line in AdminUpdate.xlsxData["pdvs"].items() if 'agent' in line['missingValues']}
    dictAgent = {}
    for idPdv, newName in dataAgent.items():
      if not newName in dictAgent:
        dictAgent[newName] = {}
      oldIdAgent = currentPdvs[idPdv][indexAgent]
      if not oldIdAgent in dictAgent[newName]:
        dictAgent[newName][oldIdAgent] = {"oldName":currentAgent[oldIdAgent], "idPdvs":[]}
      dictAgent[newName][oldIdAgent]["idPdvs"].append(idPdv)
    dictCandidate = {}
    for newName, dictOldNames in dictAgent.items():
      countOldNames = {len(dictOld["idPdvs"]):idAgent for idAgent, dictOld in dictOldNames.items()}
      indexMax = max(countOldNames, key=countOldNames.get)
      dictCandidate[newName] = {"idOld":countOldNames[indexMax], "oldName":currentAgent[countOldNames[indexMax]]}
    for newAgent, dictOldNames in dictCandidate.items():
      idOldAgent = dictOldNames["idOld"]
      if self.__agentStillExists(idOldAgent):
        del dictCandidate[newAgent]
    return dictCandidate

  def __agentStillExists(self, idOldAgent):
    for pdv in list(AdminUpdate.xlsxData["pdvs"].values()) +  AdminUpdate.xlsxData["newPdvs"]:
      if pdv["agent"] == idOldAgent:
        return True
    return False

  def updateRefWithAgent(self, getDict):
    self.__createDefaultValues(AgentSave)
    dictReplacedAgent = {oldName:value[0] for oldName, value in getDict.items() if not oldName in ["action", "csrfmiddlewaretoken"]}
    replaced, AdminUpdate.creationElement["agent"], used = [], {}, []
    currentAgent = getattr(self.dataDashboard, "__agent")
    # traitement des agent à remplacer
    for line in self.xlsxData["pdvs"].values():
      if 'agent' in line['missingValues']:
        newName = line["agent"]
        if dictReplacedAgent[newName] == "replace":
          if not newName in replaced:
            id = self.replacedAgent[newName]["idOld"]
            AgentSave.objects.create(id=id, name=newName, idF=id)
            used.append(id)
            replaced.append(newName)
          indexAgent = line['missingValues'].index('agent')
          del line['missingValues'][indexAgent]
          line["agent"] = id
          if not "differences" in line:
            line["differences"] = []
          line["differences"].append("agent")
      else:
        if not line["agent"] in used:
          name = currentAgent[line["agent"]]
          AgentSave.objects.create(id=line["agent"], name=name, idF=line["agent"])
          used.append(line["agent"])
    # Traitement des anciensPdv
    for agent in [Pdv.objects.get(id=id).agent for id in AdminUpdate.xlsxData["oldPdvs"]]:
      if not agent.id in used:
        AgentSave.objects.create(id=agent.id, name=agent.name, idF=agent.id)
        used.append(agent.id)
    # Traitement des nouveaux agents
    for line in list(AdminUpdate.xlsxData["pdvs"].values()) + AdminUpdate.xlsxData["newPdvs"]:
      if 'agent' in line['missingValues']:
        newName = line["agent"]
        if not newName in self.creationElement["agent"]:
          newAgent = AgentSave.objects.create(name=newName)
          newAgent.idF = newAgent.id
          AdminUpdate.creationElement["agent"][newName] = newAgent.id
        indexAgent = line['missingValues'].index('agent')
        del line['missingValues'][indexAgent]
        line["agent"] = self.creationElement["agent"][newName]
        if not "differences" in line:
          line["differences"] = []
        line["differences"].append("agent")
    del AdminUpdate.creationElement["agent"]
    return self.__endTreatment()

  def __endTreatment(self):
    self.__createElement()
    self.__createPdvSave()
    self.__computeNbVisits()
    self.__createRefSaveJson()
    self.__createRefJson()
    return AdminUpdate.response 

  def __createElement(self):
    for line in list(AdminUpdate.xlsxData["pdvs"].values()) + AdminUpdate.xlsxData["newPdvs"]:
      for missingField in line['missingValues']:
        value = line[missingField]
        line[missingField] = AdminUpdate.creationElement[missingField][value]
      del line['missingValues']

  def __agentFinitionsDelete(self):
    for objectModel in [PdvSave, AgentFinitionsSave]:
      self.__createDefaultValues(objectModel)

  def __createPdvSave(self):
    self.__createExistingPdvSave()
    self.__createNewPdvSave()
    self.__createCanceledPdvSave()

  def __createExistingPdvSave(self):
    for id, value in AdminUpdate.xlsxData["pdvs"].items():
      kwargs = {field:self.__computeDataForKwargs(field, data) for field, data in value.items() if not field in ['nbVisits', 'differences', 'codeNew']}
      kwargs["id"] = id
      kwargs["idF"] = id
      kwargs["agentFinitions"] = self.__computeAgentFinitionsForPdv(kwargs["dep"], kwargs["drv"])
      for fieldName in ["sale", "available", "redistributed", "redistributedFinitions", "onlySiniat", "closedAt"]:
        objectPdv = Pdv.objects.get(id=id)
        kwargs[fieldName] = getattr(objectPdv, fieldName)
      if not kwargs["available"] or not kwargs["redistributed"]:
        kwargs["segmentMarketing"] = SegmentMarketingSave.objects.get(name="Fermé")
      if "codeNew" in value:
        value["differences"].append("code")
        kwargs["code"] = value["codeNew"]
      if kwargs["closedAt"]:
        kwargs["closedAt"] = None
        kwargs["available"] = True
      PdvSave.objects.create(**kwargs)

  def __createNewPdvSave(self):
    for value in AdminUpdate.xlsxData["newPdvs"]:
      kwargs = {field:self.__computeDataForKwargs(field, data) for field, data in value.items() if not field in ['nbVisits', 'differences', 'codeNew']}
      kwargs["agentFinitions"] = self.__computeAgentFinitionsForPdv(kwargs["dep"], kwargs["drv"])
      if "codeNew" in value:
        kwargs["code"] = value["codeNew"]
      savePdv = PdvSave.objects.create(**kwargs)
      savePdv.idf = savePdv.id
      savePdv.save()

  def __createCanceledPdvSave(self):
    now = timezone.now()
    for id in AdminUpdate.xlsxData["oldPdvs"]:
      oldPdv = Pdv.objects.get(id=id)
      kwargs = {}
      kwargs = {field.name:self.__computeDataForCanceledPdv(field.name, oldPdv) for field in PdvSave._meta.fields}
      if kwargs["closedAt"]:
        if kwargs["closedAt"].year < now.year - 1:
          kwargs["available"] = False
      else:
        kwargs["closedAt"] = now
      PdvSave.objects.create(**kwargs)
      
      
  def __computeDataForCanceledPdv(self, fieldName, oldPdv):
    valueField = getattr(oldPdv, fieldName)
    if isinstance(PdvSave._meta.get_field(fieldName), models.ForeignKey):
      saveModel = PdvSave._meta.get_field(fieldName).remote_field.model
      saveObject = saveModel.objects.filter(name=valueField.name)
      if not saveObject and isinstance(valueField, Agent):
        saveObject = saveModel.objects.filter(id=valueField.id)
      return saveObject[0]
    return valueField
    

  def __computeDataForKwargs(self, field, data):
    if isinstance(PdvSave._meta.get_field(field), models.ForeignKey):
      classObject = PdvSave._meta.get_field(field).remote_field.model
      instanceObject = classObject.objects.filter(id=data)
      if instanceObject:
        return instanceObject[0]
      else:
        print("__computeDataForKwargs", field, data)
        return None
    return data

  def __computeAgentFinitionsForPdv(self, objectDep, objectDrv):
    depOld = Dep.objects.get(id=objectDep.id)
    pdvOld = Pdv.objects.filter(dep=depOld, currentYear=True).first()
    agentFinitionsOld = pdvOld.agentFinitions
    agentFinitionsList = AgentFinitionsSave.objects.filter(id=agentFinitionsOld.id)
    if agentFinitionsList:
      return agentFinitionsList[0]
    return AgentFinitionsSave.objects.create(
      id=agentFinitionsOld.id,
      name=agentFinitionsOld.name,
      drv=objectDrv,
      ratioTargetedVisit=agentFinitionsOld.ratioTargetedVisit,
      TargetedNbVisit=agentFinitionsOld.TargetedNbVisit,
      idF=agentFinitionsOld.id
      )

  def __computeNbVisits(self):
    now = timezone.now()
    self.__createDefaultValues(VisitSave)
    for id, value in AdminUpdate.xlsxData["pdvs"].items():
      if "nbVisits" in value and value["nbVisits"]:
        VisitSave.objects.create(date=now, nbVisit=value["nbVisits"], pdv=PdvSave.objects.get(id=id))
    for value in AdminUpdate.xlsxData["newPdvs"]:
      if "nbVisits" in value and value["nbVisits"]:
        id = PdvSave.objects.get(code=value["code"]).id
        VisitSave.objects.create(date=now, nbVisit=value["nbVisits"], pdv=PdvSave.objects.get(id=id))


  def __saveDataVol(self):
    self.__createDefaultValues(SalesSave)
    self.__importSiniatVolume()
    self.__importOtherVolume()

  def __createRefSaveJson(self):
    pdvs = PdvSave.objects.all()
    listName = Pdv.listFields()
    fieldsObject = [name for name in listName if getattr(Pdv, name, False) and (isinstance(Pdv._meta.get_field(name), models.ForeignKey))]
    pdvsToExport = [self.__computePdvSaveJson(pdv, fieldsObject) for pdv in pdvs]
    with open("./visioAdmin/dataFile/Json/refSave.json", 'w') as jsonFile:
      json.dump(pdvsToExport, jsonFile, indent = 3)

  def __createRefJson(self):
    pdvs = getattr(self.dataDashboard, "__pdvs")
    indexes = Pdv.listIndexes()
    listFields = Pdv.listFields()
    pdvsToExport = [self.__computePdvJson(line, listFields, indexes, self.fieldNamePdv) for line in pdvs.values()]
    with open("./visioAdmin/dataFile/Json/ref.json", 'w') as jsonFile:
      json.dump(pdvsToExport, jsonFile, indent = 3)

  def __computePdvSaveJson(self, pdv, fieldsObject):
    lineFormated = []
    for  field in self.fieldNamePdv.keys():
      fieldVal = getattr(pdv, field)
      value = "a"
      if field == "closedAt":
        value = fieldVal.strftime("%m/%d/%Y") if pdv.closedAt else ""
      elif isinstance(fieldVal, bool):
        value = "Oui" if fieldVal else "Non"
      elif field in fieldsObject:
        value = fieldVal.name
      else:
        value = fieldVal
      lineFormated.append(value)
    return lineFormated

  def __computePdvJson(self, line, listFields, indexes, fieldNamePdv):
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

  def __importSiniatVolume(self):
    siniat = Industry.objects.get(name="Siniat")
    pregy = Industry.objects.get(name="Prégy")
    salsi = Industry.objects.get(name="Salsi")
    plaque =  Product.objects.get(name="plaque")
    cloison =  Product.objects.get(name="cloison")
    doublage =  Product.objects.get(name="doublage")
    enduit = Product.objects.get(name="enduit")
    listTitlesSiniat = list(self.xlsxData["siniat"]["titles"].keys())
    listTitlesSalsi = list(self.xlsxData["salsi"]["titles"].keys())
    indexPdv = listTitlesSiniat.index("code pdv")
    indexPlaque = listTitlesSiniat.index("Plaques")
    indexCloison = listTitlesSiniat.index("Cloisons")
    indexDoublage = listTitlesSiniat.index("Doublages")
    indexPregy = listTitlesSiniat.index("Enduit Prégy")
    indexSalsi = listTitlesSalsi.index("Enduit Joint Salsi")
    dictSiniat = [{"ind":siniat, "prod":plaque, "iVol":indexPlaque}, {"ind":siniat, "prod":cloison, "iVol":indexCloison}, {"ind":siniat, "prod":doublage, "iVol":indexDoublage}, {"ind":pregy, "prod":enduit, "iVol":indexPregy}]
    for data in self.xlsxData["siniat"]["data"]:
      for dictData in dictSiniat:
        if data[dictData["iVol"]]:
          pdv = PdvSave.objects.filter(code=data[indexPdv])
          if pdv:
            SalesSave.objects.create(date=None, pdv=pdv[0], industry=dictData["ind"], product=dictData["prod"],volume=data[dictData["iVol"]])
    for data in self.xlsxData["salsi"]["data"]:
      if data[indexSalsi]:
        pdv = PdvSave.objects.filter(code=data[indexPdv])
        if pdv:
          SalesSave.objects.create(date=None, pdv=pdv[0], industry=salsi, product=enduit,volume=data[indexSalsi])

  def __importOtherVolume(self):
    listSales = [objectSales for objectSales in Sales.objects.filter(currentYear=True) if not objectSales.industry.name in ["Siniat", "Prégy", "Salsi"]]
    listField = [field.name for field in SalesSave._meta.fields if field.name != "id"]
    listKwargs = [{field:self.__findValueForOtherVolume(objectSale, field) for field in listField} for objectSale in listSales]
    for kwargs in listKwargs:
      if kwargs["pdv"]:
        SalesSave.objects.create(**kwargs)


  def __findValueForOtherVolume(self, objectSale, field):
    if field != "pdv":
      return getattr(objectSale, field)
    pdvOld = getattr(objectSale, field)
    pdvNew = PdvSave.objects.filter(code=pdvOld.code)
    if pdvNew:
      return pdvNew[0]
    return False

  def switchBase(self):
    dictTables={
      "visit":{"current":Visit, "save":VisitSave},
      "sales":{"current":Sales, "save":SalesSave},
      "pdv":{"current":Pdv, "save":PdvSave},
      "agentFinitions":{"current":AgentFinitions, "save":AgentFinitionsSave},
      "agent":{"current":Agent, "save":AgentSave},
      "dep":{"current":Dep, "save":DepSave},
      "drv":{"current":Drv, "save":DrvSave},
      "bassin":{"current":Bassin, "save":BassinSave},
      "ville":{"current":Ville, "save":VilleSave},
      "segmentCommercial":{"current":SegmentCommercial, "save":SegmentCommercialSave},
      "segmentMarketing":{"current":SegmentMarketing, "save":SegmentMarketingSave},
      "site":{"current":Site, "save":SiteSave},
      "sousEnsemble":{"current":SousEnsemble, "save":SousEnsembleSave},
      "ensemble":{"current":Ensemble, "save":EnsembleSave},
      "enseigne":{"current":Enseigne, "save":EnseigneSave},
    }
    dataTable = self.__readTable(dictTables)
    self.__eraseTableForSwitch(dictTables)
    self.__fillUpTableForSwicth(dataTable, dictTables)

    return {"switchBase":"workInProgress"}

  def __readTable(self, dictTables):
    dataTable = {"target":{}, "targetLevel":{}}
    for name, dictTable in dictTables.items():
      print("__readTable", name)
      newDict = {}
      for status, modelTable in dictTable.items():
        if status == "current" and not name in ["ville", "visit"]:
          newDict[status] = [self.__computeIdValue(modelTable, modelObject) for modelObject in modelTable.objects.filter(currentYear=True)]
          newDict["lastYear"] = [self.__computeIdValue(modelTable, modelObject) for modelObject in modelTable.objects.filter(currentYear=False)]
        else:
          newDict[status] = [self.__computeIdValue(modelTable, modelObject) for modelObject in modelTable.objects.all()]
      dataTable[name] = newDict

    dataTable["target"] ["save"]= [self.__computeIdValue(Target, modelObject) for modelObject in Target.objects.all()]
    dataTable["targetLevel"]["save"] = [self.__computeIdValue(TargetLevel, modelObject) for modelObject in TargetLevel.objects.filter(currentYear=True)]
    dataTable["targetLevel"]["lastYear"] = [self.__computeIdValue(TargetLevel, modelObject) for modelObject in TargetLevel.objects.filter(currentYear=False)]
    return dataTable

  def __computeIdValue(self, modelTable, modelObject):
    listField = [field for field in modelTable._meta.fields if field.name != "currentYear"]
    listForeign = [field for field in listField if isinstance(field, models.ForeignKey)]
    return {field.name:getattr(modelObject, field.name).id if field in listForeign and getattr(modelObject, field.name) else getattr(modelObject, field.name) for field in listField}

  def __eraseTableForSwitch(self, dictTables):
    listModel = [Target, TargetLevel] + [dictModel["current"] for dictModel in dictTables.values()] + [dictModel["save"] for dictModel in dictTables.values()]
    for model in listModel:
      print("__eraseTableForSwitch", model)
      model.objects.all().delete()
      tableName = model.objects.model._meta.db_table
      with connection.cursor() as cursor:
        cursor.execute(f"ALTER TABLE {tableName} AUTO_INCREMENT=1;")

  def __fillUpTableForSwicth(self, dataTable, dictTable):
    listTable = list(dataTable.keys())
    listTable.reverse()
    dictIdEquiv = self.__fillUpTableForSwicthCurrent(dataTable, dictTable, listTable)
    self.__fillUpTableForSwicthLastYear(dataTable, dictTable, listTable, dictIdEquiv)
    self.__fillUpTableForSwicthSave(dataTable, dictTable, listTable)

  def __fillUpTableForSwicthCurrent(self, dataTable, dictTable, listTable):
    print("start __fillUpTableForSwicthCurrent")
    dictIdEquiv = {}
    for table in listTable:
      if table in dictTable:
        self.__applySwitchCurrent(table, dictIdEquiv, dictTable[table]["current"], dataTable[table]["save"])
    self.__applySwitchCurrent("target", dictIdEquiv, Target, dataTable["target"]["save"])
    self.__applySwitchCurrent("targetLevel", dictIdEquiv, TargetLevel, dataTable["targetLevel"]["save"])
    return dictIdEquiv

  def __applySwitchCurrent(self, table, dictIdEquiv, targetTable, valueTable):
    print("table", table)
    dictIdEquiv[table] = {}
    listFieldName = [field.name for field in targetTable._meta.fields]
    for line in valueTable:
      id = line["id"]
      del line["id"]
      kwargs = {field:self.__findObjectForSwitch(field, value, dictIdEquiv, targetTable) for field, value in line.items()}
      if "currentYear" in listFieldName:
        kwargs["currentYear"] = True
      if (not "pdv" in line) or ("pdv" in line and kwargs["pdv"]):
        objectCreated = targetTable.objects.create(**kwargs)
        dictIdEquiv[table][id] = objectCreated.id
        if "idF" in listFieldName:
          objectCreated.idF = objectCreated.id
          objectCreated.save()

  def __fillUpTableForSwicthLastYear(self, dataTable, dictTable, listTable, DictIdEquivCurrent):
    print("start __fillUpTableForSwicthLastYear")
    dictIdEquiv = {}
    for table in listTable:
      if table in dictTable and "lastYear" in dataTable[table]:
        self.__applySwitchLastYear(table, dictIdEquiv, dictTable[table]["current"], dataTable[table]["lastYear"], DictIdEquivCurrent)
    self.__applySwitchLastYear("targetLevel", dictIdEquiv, TargetLevel, dataTable["targetLevel"]["lastYear"], DictIdEquivCurrent)

  def __applySwitchLastYear(self, table, dictIdEquiv, targetTable, valueTable, DictIdEquivCurrent):
    print("table", table)
    dictIdEquiv[table] = {}
    targetTable = targetTable
    listFieldName = [field.name for field in targetTable._meta.fields]
    if "currentYear" in listFieldName:
      for line in valueTable:
        id = line["id"]
        del line["id"]
        kwargs = {field:self.__findObjectForSwitch(field, self.__computeValueLastYear(field, value, DictIdEquivCurrent, targetTable), dictIdEquiv, targetTable) for field, value in line.items()}
        kwargs["currentYear"] = False
        if "idF" in listFieldName:
          if targetTable == Agent:
            if kwargs["idF"] in DictIdEquivCurrent:
              kwargs["idF"] = DictIdEquivCurrent[kwargs["idF"]]
          elif targetTable == Pdv:
            currentPdv = Pdv.objects.filter(code=kwargs["code"], currentYear=True)
            if currentPdv:
              kwargs["idF"] = currentPdv[0].id
          else:
            currentObject = targetTable.objects.filter(name=kwargs["name"])
            if currentObject:
              kwargs["idF"] = currentObject[0].id
        if (not "pdv" in line) or ("pdv" in line and kwargs["pdv"]):
          objectCreated = targetTable.objects.create(**kwargs)
          dictIdEquiv[table][id] = objectCreated.id

    elif table == "visit":
      currentYear = ParamVisio.getValue("currentYear")
      listVisit = [self.__computeKwargsVisit(visit, listFieldName, dictIdEquiv) for visit in Visit.object.all() if visit.date.year < currentYear]
      for kwargs in listVisit:
        VisitSave.object.create(**kwargs)

    elif table == "ville":
      indexVille = getattr(self.dataDashboard, "__structurePdvs").index("ville")
      existingVille = {ville.name for ville in VilleSave.objects.all()}
      print("existingVille", existingVille)
      villePast = {line[indexVille] for line in getattr(self.dataDashboard, "__pdvs_ly") if not line[indexVille] in existingVille}
      for ville in villePast:
        VilleSave.objects.create(name=ville)
      dictIdEquiv[table] = {ville.id:VilleSave.get(name=ville.name) for ville in Ville.objects.all() if  VilleSave.filter(name=ville.name)}

  def __computeKwargsVisit(self, visit, listFieldName, dictIdEquiv):
    kwargs = {}
    for field in listFieldName:
      if field != "id":
        if field == "pdv":
          newId = dictIdEquiv[visit[field].id]
          kwargs["pdv"] = newId
        else:
          kwargs[field] = visit[field]
      
  def __fillUpTableForSwicthSave(self, dataTable, dictTable, listTable):
    print("start __fillUpTableForSwicthSave")
    dictIdEquiv = {}
    for table in listTable:
      print("table", table)
      dictIdEquiv[table] = {}
      targetTable = dictTable[table]["save"]
      for line in dataTable[table]["current"]:
        id = line["id"]
        del line["id"]
        kwargs = {field:self.__findObjectForSwitch(field, value, dictIdEquiv, targetTable) for field, value in line.items()}
        objectCreated = targetTable.objects.create(**kwargs)
        dictIdEquiv[table][id] = objectCreated.id
        if "idF" in [field.name for field in targetTable._meta.fields]:
          objectCreated.idF = objectCreated.id
          objectCreated.save()

  def __findObjectForSwitch(self, fieldName, value, dictIdEquiv, targetTable):
    field = targetTable._meta.get_field(fieldName)
    if isinstance(field, models.ForeignKey) and value:
      if field.name in dictIdEquiv and value in dictIdEquiv[field.name]:
        newId = dictIdEquiv[field.name][value]
      elif  field.name in dictIdEquiv:
        print("strange case", targetTable, field.name, value)
        return None
      else:
        newId = value
      modelObject = field.remote_field.model
      objectWithId = modelObject.objects.filter(id=newId)
      if objectWithId:
        return objectWithId[0]
      print("strange case bis", field.name, value, targetTable)
      return None
    return value

  def __computeValueLastYear(self, fieldName, value, DictIdEquivCurrent, targetTable):
    field = targetTable._meta.get_field(fieldName)
    if isinstance(field, models.ForeignKey) and value:
      if field.name in DictIdEquivCurrent and value in DictIdEquivCurrent[field.name]:
        return DictIdEquivCurrent[field.name][value]
      return None
    return value








    









