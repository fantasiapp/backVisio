from sys import hash_info
from visioAdmin.dataModel.createWidgetParam import CreateWidgetParam
from dateutil import tz
from django.utils import timezone
import pytz
from datetime import datetime
import mysql.connector as db
import json
import os
from dotenv import load_dotenv
from visioServer.models import *
from django.contrib.auth.models import User, Group

load_dotenv()

class ManageFromOldDatabase:
  fieldsPdv = []
  listPdv = None
  dictDrv = {}
  dictAgent = {}
  dictAgentFinitions = {}
  dictDep = {}
  dictBassin = {}
  dictVille = {}
  dictSegco = {}
  dictSegment = {}
  dictHolding = {}
  dictProduct = {}
  dictIndustry = {}
  dictUsers = {}
  __depFinition = {
    1:[64,40,33,17,16,24,47,32,65,9,31,81,82,46,87,23],
    2:[29,22,56,35,44,85,49,53,50,14,61,72,37,79,86,36,41,18],
    3:[28,27,76,80,60,95,78,91,77,75,92,94,93],
    4:[13,84,83,4,5,6],
    5:[19,15,63,3,43,42,69,71,1,38,26,7,73,74],
    6:[66,11,34,12,30,48],
    7:[62,59,2,8,51,10,89,45,58,21,52,55,54,57,88,70,39,25,90,68,67]
    }

  typeObject = {
     "synonyms":Synonyms, "dataAdmin":DataAdmin, "paramVisio":ParamVisio, "sales":Sales, "pdv":Pdv, "targetLevel":TargetLevel, "agent":Agent, "agentFinitions":AgentFinitions,
     "dep":Dep, "drv":Drv, "bassin":Bassin, "ville":Ville, "segCo":SegmentCommercial,
    "segment":SegmentMarketing, "unused1":Site, "unused2":SousEnsemble, "unused3":Ensemble, "holding":Enseigne,"product":Product,
    "industry":Industry, "user":UserProfile, "treeNavigation":TreeNavigation, "dashBoard":Dashboard, "layout":Layout, "widgetParams":WidgetParams,
    "widgetCompute":WidgetCompute, "widget":Widget, "target":Target, "visit":Visit, "axisForGraph":AxisForGraph,
    "labelForGraph":LabelForGraph
    }
  connection = None
  cursor = None
  

  def emptyDatabase(self, start:bool) -> dict:
    if start:
      self.connectionNew = db.connect(
        user = os.getenv('DB_USERNAME'),
        password = os.getenv('DB_PASSWORD'),
        host = os.getenv('DB_HOST'),
        database = os.getenv('DB_NAME'),
      )
      self.cursorNew = self.connectionNew.cursor()
      self.typeObjectList = list(self.typeObject.values())
      for classObject in [LogUpdate, LogClient]:
        classObject.objects.all().delete()

    if self.typeObjectList:
      model = self.typeObjectList.pop(0)
      table = model.objects.model._meta.db_table

      model.objects.all().delete()
      self.cursorNew.execute(f"ALTER TABLE {table} AUTO_INCREMENT=1;")
      # Le cas d'une table Many to Many
      if model == Dashboard:
        self.cursorNew.execute(f"ALTER TABLE `visioServer_dashboard_widgetParams` AUTO_INCREMENT=1;")
      return {'query':'emptyDatabase', 'message':f"la table {table} a été vidée.", 'end':False, 'errors':[]}
    
    for user in User.objects.all():
      if not user.username in ["vivian", "jlw"]:
        user.delete()
      else:
        user.groups.clear()
    Group.objects.all().delete()
    self.cursorNew.execute("ALTER TABLE `auth_user` AUTO_INCREMENT=3;")
    self.cursorNew.execute("ALTER TABLE `auth_group` AUTO_INCREMENT=1;")
    self.connectionNew.close()
    return {'query':'emptyDatabase', 'message':"<b>La base de données a été vidée</b>", 'end':True, 'errors':[]}


  def populateDatabase(self, start:bool, method:str) -> 'list(str)':
    if start:
      ManageFromOldDatabase.connection = db.connect(
      user = os.getenv('DB_USERNAME_ORI'),
      password = os.getenv('DB_PASSWORD_ORI'),
      host = os.getenv('DB_HOST_ORI'),
      database = os.getenv('DB_NAME_ORI')
      )
      ManageFromOldDatabase.cursor = ManageFromOldDatabase.connection.cursor()
      self.dictPopulate = [
        ("PdvOld",[]), ("SynonymAdmin",[]), ("ParamVisio", []), ("Object", ["drv"]), ("Agent", []), ("Object", ["dep"]), ("Object", ["bassin"]),
        ("Object", ["industry"]), ("Object", ["product"]), ("Object", ["holding"]), ("ObjectFromPdv", ["ensemble", Ensemble]),
        ("ObjectFromPdv", ["sous-ensemble", SousEnsemble]), ("ObjectFromPdv", ["site", Site]),
        ("Object", ["ville"]), ("Object", ["segCo"]), ("Object", ["segment"]), ("AgentFinitions", []), ("PdvNew", []), ("Users", []),
        ("TreeNavigation", [["geo", "trade"]]),
        ("Target", []), ("TargetLevel", []), ("Visit", []), ("Sales", [])]
    if self.dictPopulate:
      tableName, variable = self.dictPopulate.pop(0)
      print(tableName, variable[0] if  len(variable) > 0 else '')
      table, error = getattr(self, "get" + tableName)(*variable)
      error = [error] if error else []
      message = "L'ancienne base de données est lue" if tableName == "PdvOld" else f"La table {str(table)} est remplie "
      return {'query':method, 'message':message, 'end':False, 'errors':error}
    ManageFromOldDatabase.connection.close()
    return {'query':method, 'message':"<b>La base de données a été remplie</b>", 'end':True, 'errors':[]}

  def getSynonymAdmin(self):
    with open("./visioAdmin/dataFile/Json/SynParam.json") as jsonFile:
      data = json.load(jsonFile)
    classDict = {"Synonyms":Synonyms, "dataAdmin":DataAdmin}
    for key, kwargslist in data.items():
      for kwargs in kwargslist:
        classDict[key].objects.create(**kwargs)
    return ("Synonyms", False)

  
  def getPdvOld(self):
    if not self.listPdv:
      self.listPdv = {"lastYear":[], "currentYear":[]}
      try:
        query = "SHOW COLUMNS FROM ref_pdv_1"
        ManageFromOldDatabase.cursor.execute(query)
        self.fieldsPdv = [field[0] for field in ManageFromOldDatabase.cursor]
      except db.Error as e:
        return (False, "getPdvOld for fields " + repr(e))
      for number, name in {0:"lastYear", 1:"currentYear"}.items():
        try:
          query = f"SELECT * FROM ref_pdv_{number} WHERE `Closed_by_OM` <> 'y'"
          ManageFromOldDatabase.cursor.execute(query)
          for line in ManageFromOldDatabase.cursor:
            line = [self.unProtect(item) for item in line]
            self.listPdv[name].append(line)
        except db.Error as e:
          return (False, "getPdvOld for values " + repr(e))
    return (False, False)

  def getPdvNew(self):
    dictDepIdFinition = self.__computeDepIdFinition()
    listYear, self.__dictIdNewId, self.__dictNameNewId = ["lastYear", "currentYear"], {}, {}
    for indexYear in [1,0]:
      year = listYear[indexYear]
      for line in self.listPdv[year]:
        keyValues = {}
        keyValues["drv"] = self.__findObject("id_drv", self.dictDrv, year, line, Drv)
        keyValues["agent"] = self.__findObject("id_actor", self.dictAgent, year, line, Agent)
        keyValues["dep"] = self.__findObject("id_dep", self.dictDep, year, line, Dep)
        keyValues["agentFinitions"] = AgentFinitions.objects.get(id=dictDepIdFinition[keyValues["dep"].id])
        keyValues["bassin"] = self.__findObject("id_bassin", self.dictBassin, year, line, Bassin)
        keyValues["ville"] = self.__findObject("id_ville", self.dictVille, year, line, Ville)
        keyValues["enseigne"] = self.__findObject("id_holding", self.dictHolding, year, line, Enseigne)
        keyValues["ensemble"] = Ensemble.objects.filter(name__iexact=line[self.fieldsPdv.index("ensemble")], currentYear=indexYear==1).first()
        keyValues["sousEnsemble"] = SousEnsemble.objects.filter(name__iexact=line[self.fieldsPdv.index("sous-ensemble")], currentYear=indexYear==1).first()
        keyValues["site"] = Site.objects.filter(name__iexact=line[self.fieldsPdv.index("site")], currentYear=indexYear==1).first()
        keyValues["segmentCommercial"] = self.__findObject("id_segCo", self.dictSegco, year, line, SegmentCommercial)
        keyValues["segmentMarketing"] = self.__findObject("id_segment", self.dictSegment, year, line, SegmentMarketing)
        keyValues["code"] = line[self.fieldsPdv.index("PDV code")] if line[self.fieldsPdv.index("PDV code")] else None
        keyValues["name"] = line[self.fieldsPdv.index("PDV")] if line[self.fieldsPdv.index("PDV")] else None
        keyValues["latitude"] = line[self.fieldsPdv.index("latitude")] if line[self.fieldsPdv.index("PDV code")] else None
        keyValues["longitude"] = line[self.fieldsPdv.index("longitude")] if line[self.fieldsPdv.index("PDV")] else None
        keyValues["available"] = self.__computeBoolean(line, field="does_not_exist", valueIfNotExist="y")
        keyValues["sale"] = self.__computeBoolean(line, field="sale", valueIfNotExist="y")
        keyValues["redistributed"] = self.__computeBoolean(line, field="redistributed", valueIfNotExist="y")
        keyValues["redistributedFinitions"] = self.__computeBoolean(line, field="redistributedEnduit", valueIfNotExist="y")
        keyValues["pointFeu"] = self.__computeBoolean(line, field="pointFeu", valueIfNotExist="O", inverse=True)
        keyValues["closedAt"] = self.__computeClosedAt(line)
        keyValues["currentYear"] = indexYear==1

        for field, object in keyValues.items():
          if object == None and field != "closedAt":
            return [False, "field {}, Pdv {}, code {} does not exist".format(field, keyValues["name"], keyValues["code"])]
        existsPdv = Pdv.objects.filter(code=keyValues["code"], currentYear=indexYear==1)
        if not existsPdv.exists():
          pdv = Pdv.objects.create(**keyValues)
          self.setIdF(pdv, True, pdv.code, None, indexYear)
        else:
          return (False, "Pdv {}, code {} allready exists".format(keyValues["name"], keyValues["code"]))
    return ("Pdv", False)

  def __computeDepIdFinition(self):
    depFinition = self.__depFinition
    listDepIdFinition = {}
    for currentYear in [True, False]:
      if not currentYear:
        decal = len(depFinition)
        depFinition = {id + decal:value for id, value in depFinition.items()}
      dictDep = {dep.name:dep.id for dep in Dep.objects.filter(currentYear=currentYear)}
      for idFinition, listDep in depFinition.items():
        listDepStr = {str(dep) if dep > 9 else f"0{str(dep)}" for dep in listDep}
        listDepId = [dictDep[depName] for depName in listDepStr]
        for idDep in listDepId:
          listDepIdFinition[idDep] = idFinition
    return listDepIdFinition

  def __computeBoolean(self, line:list, field:str, valueIfNotExist:str, inverse:bool=False) -> bool:
    valueFound = line[self.fieldsPdv.index(field)]
    return valueFound == valueIfNotExist if inverse else valueFound != valueIfNotExist

  def __computeClosedAt(self, line:list):
    timestamp = line[self.fieldsPdv.index("toBeClosed")]
    if timestamp:
      return datetime.datetime.fromtimestamp(timestamp, tz=tz.gettz("Europe/Paris"))
    return None

  def __findObject(self, fieldName, dico, year, line, model):
    indexObject =  self.fieldsPdv.index(fieldName)
    idObject = line[indexObject]
    if year in dico:
      nameObject = dico[year][idObject] if idObject in dico[year] else dico[year][1]
    else:
      nameObject = dico[idObject] if idObject in dico else dico[1]
    if getattr(model, "currentYear", False):
      objectFound = model.objects.filter(name=nameObject, currentYear=year=="currentYear")
    else:
      objectFound = model.objects.filter(name=nameObject)
    return objectFound.first() if objectFound.exists() else None

  def getAgent(self):
    listYear, self.__dictIdNewId, self.__dictNameNewId = ["lastYear", "currentYear"], {}, {}
    try:
      for indexYear in [1,0]:
        query = f"SELECT id, name FROM ref_actor_{indexYear}"
        ManageFromOldDatabase.cursor.execute(query)
        for (id, name) in ManageFromOldDatabase.cursor:
          existAgent = Agent.objects.filter(name__iexact=name, currentYear=indexYear == 1)
          if not existAgent.exists():
            agent = Agent.objects.create(name=name, currentYear=indexYear == 1)
            self.setIdF(agent, True, name, id, indexYear)
          if not listYear[indexYear] in self.dictAgent:
            self.dictAgent[listYear[indexYear]] = {}
          self.dictAgent[listYear[indexYear]][id] = name
    except db.Error as e:
      return "Error getAgent" + repr(e)
    return ("Agent", False)

  def getAgentFinitions(self):
    listYear, self.__dictIdNewId, self.__dictNameNewId = ["lastYear", "currentYear"], {}, {}
    try:
      for indexYear in [1,0]:
        query = "SELECT id, name, id_drv FROM ref_finition_1"
        ManageFromOldDatabase.cursor.execute(query)
        for (id, name, idDrv) in ManageFromOldDatabase.cursor:
          drv = Drv.objects.get(name=self.dictDrv[listYear[indexYear]][idDrv], currentYear=indexYear==1)
          existsAgent = AgentFinitions.objects.filter(name__iexact=name, currentYear=indexYear==1)
          if not existsAgent.exists():
            agent = AgentFinitions.objects.create(name=name, drv=drv, currentYear=indexYear==1)
            self.setIdF(agent, True, name, id, indexYear)
          self.dictAgentFinitions[id] = name
    except db.Error as e:
      return "Error getAgentFinitions" + repr(e)
    return ("AgentFinitions", False)

  def __cleanEnseigne(self, idEnseigne:int, nameEnsemble:str) ->str:
    if nameEnsemble == "BIGMAT FRANCE": return 1 #CMEM
    elif nameEnsemble == "PROSPECTS AD CMEM": return 1
    elif "POINT P " in nameEnsemble: return 2 #SGBD France
    elif "CHAUSSON MATERIAUX" in nameEnsemble: return 11 #Chausson
    elif "GEDIMAT" in nameEnsemble: return 3 #Gédimat
    elif "EX-" in nameEnsemble: return 9 # Nég ancien PdV
    elif nameEnsemble == "DMBP": return 2 # SGBD France
    elif nameEnsemble == "PROSPECTS SGBD FRANCE": return 2  #SGBD France
    elif nameEnsemble == "RÉSEAU PRO GRAND OUEST": return 13 # Bois et matériaux
    elif nameEnsemble == "RÉSEAU PRO IDF NORD EST": return 13 # Bois et matériaux
    elif nameEnsemble == "LITT DIFFUSION": return 5 # Sig France
    elif nameEnsemble == "PANOFRANCE": return 5 # Sig France
    elif nameEnsemble == "CIFFREO BONA": return 4 # Groupement régionaux
    elif nameEnsemble == "UNION MATERIAUX GROUPE": return 10 #Altéral
    elif nameEnsemble == "PROSPECTS AD EX NEGOCE": return 9 # Nég ancien PdV
    elif nameEnsemble == "GROUPE SAMSE": return 7 # MCD
    return idEnseigne

  def getObjectFromPdv(self, field, classObject):
    listYear, self.__dictIdNewId, self.__dictNameNewId = ["lastYear", "currentYear"], {}, {}
    dico = [[], []]
    for indexYear in [1,0]:
      IndexField = self.fieldsPdv.index(field)
      dico[indexYear] = ['Not assigned']
      classObject.objects.create(name='Not assigned', currentYear=indexYear==1)
      for line in self.listPdv[listYear[indexYear]]:
        nameField = line[IndexField]
        if not nameField in dico[indexYear]:
          dico[indexYear].append(nameField)
          newObject = classObject.objects.create(name=nameField, currentYear=indexYear==1)
          self.setIdF(newObject, True, nameField, None, indexYear)
    return (classObject.__name__, False)

  def getObject(self, nature:str):
    listYear, self.__dictIdNewId, self.__dictNameNewId = ["lastYear", "currentYear"], {}, {}
    hasLastYear = hasattr(self.typeObject[nature], "currentYear") != False
    try:
      for indexYear in [1,0]:
        if indexYear == 1 or hasLastYear:
          query = f"SELECT id, name FROM ref_{nature}_{indexYear}"
          ManageFromOldDatabase.cursor.execute(query)
          for id, name in self.computeHoldingOrder(ManageFromOldDatabase.cursor, nature):
            if nature == "industry" and name == "Pregy": name = "Prégy" 
            name, currentYear = self.unProtect(name), listYear[indexYear] == "currentYear"
            kwargs = {"name__iexact":name, "currentYear":currentYear} if getattr(self.typeObject[nature], "currentYear", False) else {"name__iexact":name}
            existobject = self.typeObject[nature].objects.filter(**kwargs)
            if not existobject.exists():
              kwargs = {"name":name, "currentYear":currentYear} if getattr(self.typeObject[nature], "currentYear", False) else {"name":name}
              newObject = self.typeObject[nature].objects.create(**kwargs)
              self.setIdF(newObject, hasLastYear, name, id, indexYear)
            dict = getattr(self, "dict" + nature.capitalize())
            if nature in ["ville", "product", "industry"] and not id in dict:
              dict[id] = name
            else:
              if not listYear[indexYear] in dict:
                dict[listYear[indexYear]] = {}
              dict[listYear[indexYear]][id] = name
    except db.Error as e:
      return (False, f"Error getObject {nature} {repr(e)}")
    return (nature, False)

  def setIdF(self, newObject, hasLastYear, name, id, indexYear):
    if hasLastYear:
      if indexYear:
        self.__dictIdNewId[id] = newObject.id
        self.__dictNameNewId[name] = newObject.id
        newObject.idF = newObject.id
        newObject.save()
      else:
        newId = self.__dictNameNewId[name] if name in self.__dictNameNewId else False
        if not newId:
          newId = self.__dictIdNewId[id] if id in self.__dictIdNewId else False
        if newId:
          newObject.idF = newId
        else:
          newObject.idF = newObject.id
        newObject.save()
    

  def computeHoldingOrder(self, cursor, nature):
    if nature != "holding":
      return cursor
    dataWithOrder = ["CMEM", "POINT P", "MCD", "Chausson", "Gédimat", "SFIC","SIG France","Bois & Mat.","Nég Mtx Cons","Group. Rég.","Altéral",
              "La Platef.","Nég ancien PdV","DMBP","SGDB France","Négoce Platec","Autres","Non identifié"]
    dictId = {}
    for (id, name) in cursor:
      if not name in dataWithOrder:
        dataWithOrder.append(name)
      dictId[name] = id
    return [(dictId[dataWithOrder[index]], dataWithOrder[index]) for index in range(len(dataWithOrder))]
  

# Création des données de navigation
  def getTreeNavigation(self, geoOrTradeList:list):
    dictGroup = {"root":"National", "drv":"Région", "agent":"Secteur", "agentFinitions":"Agent Finition"}
    listGroup = [Group.objects.get(name=name) for name in dictGroup.keys()]
    for currentYear in [True, False]:
      for geoOrTrade in geoOrTradeList:
        if currentYear == True:
          self.createDashboards(geoOrTrade)
        listLevel = self.__createNavigationLevelName(geoOrTrade)
        for group in listGroup:        
          father = None
          for levelName, prettyPrint in listLevel:
            listDashboardName = CreateWidgetParam.dashboardsLevel[geoOrTrade][levelName]
            listDashboard = [Dashboard.objects.get(name=name, geoOrTrade=geoOrTrade) for name in listDashboardName if self.filterTreeNav(name, geoOrTrade, currentYear, group.name)]
            if geoOrTrade == "trade" and levelName == "root":
              levelName, prettyPrint =group.name, dictGroup[group.name]
            subLevel = TreeNavigation.objects.create(geoOrTrade=geoOrTrade, levelName=levelName, prettyPrint=prettyPrint, currentYear=currentYear, profile=group)
            for dashboard in listDashboard:
                subLevel.listDashboards.add(dashboard)
            if father:
              father.subLevel = subLevel
              father.save()
            father = subLevel
          if geoOrTrade == "geo":
            if group.name == "agent":
              listLevel[0] = ("agentFinitions", "Agent Finition")
            else:
              listLevel.pop(0)
    return ("TreeNavigation", False)

  def filterTreeNav(self, name, geoOrTrade, currentYear, profile):
    if profile == "agent" and name == 'PdM Enduit Simulation':
      return False
    if profile == "agentFinitions" and name in ['PdM P2CD Simulation', 'DN P2CD Simulation']:
      return False
    if geoOrTrade == "trade" and name in ["Synthèse P2CD", "Synthèse Enduit"]:
      return False
    if not currentYear:
      if "Simulation" in name:
        return False
      if name in ["Suivi AD", "Suivi des Visites"]:
        return False
    return True

  def __createNavigationLevelName(self, geoOrTrade:str):
    geoTreeStructure = json.loads(os.getenv('GEO_TREE_STRUCTURE')) if geoOrTrade == "geo" else json.loads(os.getenv('TRADE_TREE_STRUCTURE'))
    fields, listLevelName = Pdv._meta.fields, []
    for fieldId in geoTreeStructure:
      listLevelName.append((fields[fieldId + 1].name, fields[fieldId + 1].verbose_name))
    return [("root", "National")] + listLevelName

  def createDashboards(self, geoOrTrade):
    if geoOrTrade == "geo":
      CreateWidgetParam.initialize()
    for value in CreateWidgetParam.dashBoardsList[geoOrTrade]:
      name, layoutName, comment = value[0], value[1], value[2]
      comment = json.dumps(comment if isinstance(comment, list) else [comment])
      object = Dashboard.objects.create(name=name, geoOrTrade=geoOrTrade, layout=CreateWidgetParam.dictLayout[layoutName], comment=comment)
      templateFlat = []
      for listPos in json.loads(CreateWidgetParam.dictLayout[layoutName].template):
        templateFlat += listPos
      listWidgetParam = CreateWidgetParam.create(name, geoOrTrade)
      for widgetParam in listWidgetParam[:len(set(templateFlat))]:
        object.widgetParams.add(widgetParam)

# Chargement de la table des Sales
  def getSales(self):
    listYear = ["lastYear", "currentYear"]
    indexCode = self.fieldsPdv.index("PDV code")
    try:
      for indexYear in range(2):
        year = listYear[indexYear]
        dictPdv = {line[0]:line for line in self.listPdv[year]}
        query = f"SELECT timestamp, id_pdv, id_industry, id_product, volume FROM data_ad_{indexYear}"
        ManageFromOldDatabase.cursor.execute(query)
        for line in ManageFromOldDatabase.cursor:
            if line[4] != 0.0 and line[1] in dictPdv:
              idOld = line[1]
              code = dictPdv[idOld][indexCode]
              pdv = Pdv.objects.filter(code=code, currentYear=indexYear==1).first()
              industry = self.dictIndustry[line[2]]
              industry = Industry.objects.filter(name=industry).first()
              product = self.dictProduct[line[3]]
              product = Product.objects.filter(name=product).first()
              dateEvent = None
              cy = indexYear == 1
              if line[0]:
                dateEvent = datetime.datetime.fromtimestamp(line[0], tz=tz.gettz("Europe/Paris"))
              Sales.objects.create(date=dateEvent, pdv=pdv, industry=industry, product=product, volume=float(line[4]), currentYear=cy)
    except db.Error as e:
      return (False, f"Error getSales {type} {repr(e)}")
    return ("Sales", False)


# Chargement de la table des utilisateurs
  def getUsers(self):
    dictUser = self.__computeListUser()
    Group.objects.create(name="root")
    for user in User.objects.all():
      user.groups.add(Group.objects.get(name="root"))
      UserProfile.objects.create(user=user, idGeo=0)
    for username, userList in dictUser.items():
      user = User.objects.create_user(username=username, password=userList[2])
      groupName = userList[0]
      if not Group.objects.filter(name=groupName):
        Group.objects.create(name=groupName)
      user.groups.add(Group.objects.get(name=groupName))
      UserProfile.objects.create(user=user, idGeo=int(userList[1]) if int(userList[1]) else 0)
    return ("Users", False)

  def __computeListUser(self):
    query = "SELECT `userPseudo`, `profile`, `userCriptedPassword` FROM user;"
    ManageFromOldDatabase.cursor.execute(query)
    dictUser = {line[0]:[line[1], line[2]] for line in ManageFromOldDatabase.cursor}

    data, table, listUser = {"drv":{}, "actor":{}, "finition":{}}, {"drv":{}, "actor":{}, "finition":{}}, {}
    for field in data.keys():
      query = f'SELECT `{"id_drv" if field == "finition" else "id"}`, `name` FROM `ref_{field}_0`;'
      ManageFromOldDatabase.cursor.execute(query)
      data[field] = {line[0]:line[1] for line in ManageFromOldDatabase.cursor}
      newField = field if field == "drv" else "agent"
      if field == "finition":
        newField = "agentFinitions"
      for oldId, name in data[field].items():
        newObject = self.typeObject[newField].objects.filter(name=name, currentYear=True).first()
        if newObject:
          table[field][oldId] = newObject.id
      table[newField] = table[field]
    del table["actor"]
    del table["finition"]
    dictEquiv = {"All":"root", "DRV":"drv", "Secteur":"agent", "Finition":"agentFinitions"}
    for pseudo, profilePassword in dictUser.items():
      profile = profilePassword[0]
      listProfile = list(profile.split(":"))
      typeTable = dictEquiv[listProfile[0]]
      oldId = int(listProfile[2])
      listData = [typeTable, table[typeTable][oldId] if typeTable in table and oldId in table[typeTable] else 0, profilePassword[1]]
      listUser[pseudo] = listData
    self.__addPassword(listUser)
    return listUser

  def __addPassword(self, listUser):
    dictUserPassword= {
      "15061218431128704":"avisio",
      "15077873162974986":"sevisio",
      "159836747134726566":"idfvisio",
      "14927206322893480":"idfvisio",
      "00082159275353182":"sovisio",
      "57510435180997040":"ovisio",
      "125249184165909318":"ravisio",
      "17071071491587506":"evisio",
      "144638294155639156":"nevisio",
      "116346511173146016":"avignon", # mot de passe de Chapat
    }
    dictUserPb = {
      "frsijmant":"sovisio",
      "chaudesaigues":"nevisio",
    }
    for pseudo, user in listUser.items():
      if pseudo in dictUserPb:
        password = dictUserPb[pseudo]
      else:
        password = dictUserPassword[user[2]] if user[2] in dictUserPassword else "natvisio"
      user[2] = password

# Chargement de la table des Sales
  def getTarget(self):
    dictPdv = {line[0]:line for line in self.listPdv["currentYear"]}
    indexCode = self.fieldsPdv.index("PDV code")
    try:
      query = "SELECT timestamp, id_pdv, depot, sale, targetVolume, targetFinition, greenLight, commentTarget FROM ciblage;"
      ManageFromOldDatabase.cursor.execute(query)
      for line in ManageFromOldDatabase.cursor:
        idOld = line[1]
        if idOld in dictPdv:
          kwargs = {}
          kwargs['date'] = datetime.datetime.fromtimestamp(line[0], tz=tz.gettz("Europe/Paris")) if line[0] else None
          code = dictPdv[idOld][indexCode]
          kwargs['pdv'] = Pdv.objects.filter(code=code, currentYear=True).first()
          kwargs['redistributed'] = line[2] != "does not exist"
          kwargs['redistributedFinitions'] = True
          kwargs['sale'] = line[3] != "does not exist"
          kwargs['targetP2CD'] = float(line[4]) if float(line[4]) else 0.0
          kwargs['targetFinitions'] = line[5] == "yes"
          kwargs['greenLight'] = line[6][0]
          kwargs['commentTargetP2CD'] = self.unProtect(line[7])
          kwargs['bassin'] = ""
          Target.objects.create(**kwargs)

    except db.Error as e:
      return (False, f"Error getTarget {repr(e)}")
    return ("Target", False)

  def getTargetLevel(self):
    volP2CD, dnP2CD, volFinition = 1000.0, 50, 150
    now = timezone.now()
    for currentYear in [True, False]:
      dictAgent = {}
      listDrv = {drv.id:drv for drv in Drv.objects.filter(currentYear=currentYear)}
      for id, drv in listDrv.items():
        dictAgent[id] = set([pdv.agent for pdv in Pdv.objects.filter(sale=True, currentYear=currentYear, drv=drv)])
      for drvId, listAgent in dictAgent.items():
        drv = listDrv[drvId]
        TargetLevel.objects.create(date=now, drv=drv, vol=volP2CD, dn=dnP2CD, currentYear=currentYear)
        dvP2CD = volP2CD / len(listAgent)
        ddP2CD, rdP2CD = dnP2CD // len(listAgent), dnP2CD % len(listAgent)
        dvFinition = volFinition / len(listAgent)
        flagStart = True
        for agent in listAgent:
          if flagStart:
            flagStart = False
            TargetLevel.objects.create(date=now, agent=agent, vol=dvP2CD, dn=ddP2CD + rdP2CD, currentYear=currentYear)
          else:
            TargetLevel.objects.create(date=now, agent=agent, vol=dvP2CD, dn=ddP2CD, currentYear=currentYear)
      listAgentFinitions = AgentFinitions.objects.filter(currentYear=currentYear)
      dvFinition = volFinition / len(listAgentFinitions)
      for agentFinition in listAgentFinitions:
          TargetLevel.objects.create(date=now, agentFinitions=agentFinition, vol=dvFinition, dn=0, currentYear=currentYear)
    return ("TargetLevel", False)

  def getVisit(self):
    query = "SELECT pdvCode, NbVisit FROM data_visit_1;"
    ManageFromOldDatabase.cursor.execute(query)
    for line in ManageFromOldDatabase.cursor:
      pdv = Pdv.objects.filter(code=line[0], currentYear=True)
      if pdv:
        for key, nbVisit in json.loads(self.unProtect(line[1])).items():
          nbVisit = int(nbVisit) if isinstance(nbVisit, str) else nbVisit
          if nbVisit != 0:
            year, month = [int(element) for element in key.split(":")]
            month = 1 if month == 0 else month
            dateVisit = date(year=year, month=month, day=1)
            Visit.objects.create(date=dateVisit, nbVisit=nbVisit, pdv=pdv[0])
    return ("Visit", False)

# Paramètres

  def getParamVisio(self):
    jsonData = {
      "enduitAxis":['enduitIndustry', 'segmentDnEnduit', 'segmentDnEnduitTarget', 'enduitIndustryTarget'],
      "nonRegularAxis":['mainIndustries', 'enduitIndustry', 'segmentDnEnduit', 'clientProspect', 'clientProspectTarget', 'segmentDnEnduitTarget', 'segmentDnEnduitTargetVisits', 'enduitIndustryTarget', 'industryTarget', 'suiviAD', 'weeks'],
      "dnIndicators":['dn', 'visits', 'targetedVisits', 'avancementAD'],
      "rodAfterFirstCategAxis":['industryTarget', 'clientProspectTarget'],
      "rodAfterSecondCategAxis":['enduitIndustryTarget'],
      "dnLikeAxis":['segmentDnEnduit', 'clientProspect', 'clientProspectTarget', 'segmentDnEnduitTarget', 'segmentDnEnduitTargetVisits', 'suiviAD', 'weeks']
      }
    ParamVisio.objects.create(field="referentielVersion", prettyPrint="Référentiel Version", fvalue="1.0.0", typeValue="str")
    ParamVisio.objects.create(field="softwareVersion", prettyPrint="Logiciel Version", fvalue="4.0.0", typeValue="str")
    ParamVisio.objects.create(field="coeffGreenLight", prettyPrint="Coefficient feu tricolore", fvalue="2", typeValue="float")
    ParamVisio.objects.create(field="ratioPlaqueFinition", prettyPrint="Ratio Plaque Enduit", fvalue="0.370", typeValue="float")
    ParamVisio.objects.create(field="ratioCustomerProspect", prettyPrint="Ratio Client Prospect", fvalue="0.1", typeValue="float")
    ParamVisio.objects.create(field="currentMonth", prettyPrint="Mois Courant", fvalue="novembre", typeValue="str")
    ParamVisio.objects.create(field="currentYear", prettyPrint="Année Courante", fvalue="2021", typeValue="int")
    ParamVisio.objects.create(field="isAdOpen", prettyPrint="Ouverture de l'AD", fvalue="True", typeValue="bool")
    ParamVisio.objects.create(field="delayBetweenUpdates", prettyPrint="Délai entre deux mise à jour", fvalue="10.0", typeValue="float")
    ParamVisio.objects.create(field="json", prettyPrint="Json", fvalue=json.dumps(jsonData), typeValue="json")
    return ("ParamVisio", False)


# Utilitaires

  def unProtect(self, string):
    if type(string) == str:
      protectDict = {"@":"<£arobase>", "\n":"<£newLine>", "&":"<£andCommercial>", "'":"<£quote>", "\t":"<£tab>", "\\":"<£backSlash>", "\"":"<£doubleQuote>", ".":"<£dot>", "/":"<£slash>", "?":"<£questionMark>", "`":"<£backQuote>", ";":"<£semicolon>", ",":"<£coma>"}
      for (symbol, protect) in protectDict.items():
        string = string.replace(protect, symbol)
      string = string.replace("  ", " ")
      return string.strip()
    return string

  def test(self):
    # listModel = [TreeNavigation, Dashboard, WidgetParams, WidgetCompute, Widget, Layout, AxisForGraph, LabelForGraph]
    # for model in listModel:
    #   model.objects.all().delete()
    print("start")
    # TargetLevel.objects.all().delete()
    # self.getTargetLevel()
    # manageFromOldDatabase.getTreeNavigation(["geo", "trade"])
    dictSyn = [{"field":obj.field, "originalName":obj.originalName, "synonym":obj.synonym} for obj in Synonyms.objects.all()]
    dictAdmin = [{"dateRef":obj.dateRef.__str__() if obj.dateRef else None, "currentBase":obj.currentBase, "fileNameRef":obj.fileNameRef, "version":obj.version, "dateVol":obj.dateVol.__str__() if obj.dateVol else None, "fileNameVol":obj.fileNameVol} for obj in DataAdmin.objects.all()]
    with open("./visioAdmin/dataFile/Json/SynParam.json", 'w') as jsonFile:
      json.dump({"Synonyms":dictSyn, "dataAdmin":dictAdmin}, jsonFile, indent = 3)
    with open("./visioAdmin/dataFile/Json/SynParam.json") as jsonFile:
      data = json.load(jsonFile)
    for kwargs in data["dataAdmin"]:
      del kwargs["id"]
      DataAdmin.objects.create(**kwargs)
    print("end")
    return {"test":False}

manageFromOldDatabase = ManageFromOldDatabase()