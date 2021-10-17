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
    8:[64,40,33,17,16,24,47,32,65,9,31,81,82,46,87,23],
    9:[29,22,56,35,44,85,49,53,50,14,61,72,37,79,86,36,41,18],
    10:[28,27,76,80,60,95,78,91,77,75,92,94,93],
    11:[13,84,83,4,5,6],
    12:[19,15,63,3,43,42,69,71,1,38,26,7,73,74],
    13:[66,11,34,12,30,48],
    14:[62,59,2,8,51,10,89,45,58,21,52,55,54,57,88,70,39,25,90,68,67]
    }

  typeObject = {
     "paramVisio":ParamVisio, "ventes":Ventes, "pdv":Pdv, "ciblageLevel":CiblageLevel, "agent":Agent, "agentfinitions":AgentFinitions, "dep":Dep, "drv":Drv, "bassin":Bassin, "ville":Ville, "segCo":SegmentCommercial,
    "segment":SegmentMarketing, "unused1":Site, "unused2":SousEnsemble, "unused3":Ensemble, "holding":Enseigne,"product":Produit,
    "industry":Industrie, "Tableaux Navigation":DashboardTree, "treeNavigation":TreeNavigation, "user":UserProfile,
    "dashBoard":Dashboard, "layout":Layout, "widgetParams":WidgetParams, "widgetCompute":WidgetCompute, "widget":Widget,
    "ciblage":Ciblage, "visit":Visit, "axisForGraph":AxisForGraph, "labelForGraph":LabelForGraph
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
      if model == DashboardTree:
        self.cursorNew.execute(f"ALTER TABLE `visioServer_dashboardtree_dashboards` AUTO_INCREMENT=1;")
      if model == Dashboard:
        self.cursorNew.execute(f"ALTER TABLE `visioServer_dashboard_widgetParams` AUTO_INCREMENT=1;")
      return {'query':'emptyDatabase', 'message':f"la table {table} a été vidée.", 'end':False, 'errors':[]}
    
    for user in User.objects.all():
      if not user.username in ["vivian", "jlw"]:
        user.delete()
    self.cursorNew.execute("ALTER TABLE `auth_user` AUTO_INCREMENT=3;")
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
        ("PdvOld",[]), ("ParamVisio", []), ("Object", ["drv"]), ("Agent", []), ("Object", ["dep"]), ("Object", ["bassin"]), ("Object", ["holding"]), ("ObjectFromPdv", ["ensemble", Ensemble]),
        ("ObjectFromPdv", ["sous-ensemble", SousEnsemble]), ("ObjectFromPdv", ["site", Site]),
        ("Object", ["ville"]), ("Object", ["segCo"]), ("Object", ["segment"]), ("AgentFinitions", []), ("PdvNew", []),
        ("Object", ["product"]), ("Object", ["industry"]), ("Ventes", []), ("TreeNavigation", [["geo", "trade"]]), ("Users", []),
        ("Ciblage", []), ("CiblageLevel", []), ("Visit", [])]
    if self.dictPopulate:
      tableName, variable = self.dictPopulate.pop(0)
      table, error = getattr(self, "get" + tableName)(*variable)
      error = [error] if error else []
      message = "L'ancienne base de données est lue" if tableName == "PdvOld" else f"La table {str(table)} est remplie "
      return {'query':method, 'message':message, 'end':False, 'errors':error}
    ManageFromOldDatabase.connection.close()
    return {'query':method, 'message':"<b>La base de données a été remplie</b>", 'end':True, 'errors':[]}

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
    listYear = ["lastYear", "currentYear"]
    for indexYear in range(2):
      year = listYear[indexYear]
      for line in self.listPdv[year]:
        keyValues = {}
        keyValues["drv"] = self.__findObject("id_drv", self.dictDrv, year, line, Drv)
        keyValues["agent"] = self.__findObject("id_actor", self.dictAgent, year, line, Agent)
        # keyValues["agentFinitions"] = self.__computeFinition("id_actor", self.dictAgent, year, line, Agent)
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
        keyValues["redistributedEnduit"] = self.__computeBoolean(line, field="redistributedEnduit", valueIfNotExist="y")
        keyValues["pointFeu"] = self.__computeBoolean(line, field="pointFeu", valueIfNotExist="O", inverse=True)
        keyValues["closedAt"] = self.__computeClosedAt(line)
        keyValues["currentYear"] = indexYear==1

        for field, object in keyValues.items():
          if object == None and field != "closedAt":
            return [False, "field {}, Pdv {}, code {} does not exist".format(field, keyValues["name"], keyValues["code"])]
        existsPdv = Pdv.objects.filter(code=keyValues["code"], currentYear=indexYear==1)
        if not existsPdv.exists():
          Pdv.objects.create(**keyValues)
        else:
          return (False, "Pdv {}, code {} allready exists".format(keyValues["name"], keyValues["code"]))
    # self.__insertAgentFinitionInPdv()
    return ("Pdv", False)

  def __insertAgentFinitionInPdv(self):
    dictDepIdFinition = self.__computeDepIdFinition()
    listPdv = Pdv.objects.all()
    for pdv in listPdv:
      agentFinitions = AgentFinitions.objects.get(id=dictDepIdFinition[pdv.dep.id])
      pdv.agentFinitions = agentFinitions
      pdv.save()

  def __computeDepIdFinition(self):
    listDepIdFinition = {}
    for currentYear in [True, False]:
      if not currentYear:
        decal = len(self.__depFinition)
        self.__depFinition = {id - decal:value for id, value in self.__depFinition.items()}
      dictDep = {dep.name:dep.id for dep in Dep.objects.filter(currentYear=currentYear)}
      for idFinition, listDep in self.__depFinition.items():
        listDepStr = {str(dep) if dep > 9 else f"0{str(dep)}" for dep in listDep}
        listDepId = [dictDep[depName] for depName in listDepStr]
        for idDep in listDepId:
          listDepIdFinition[idDep] = idFinition
    # result = dict(sorted(listDepIdFinition.items()))
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
    listYear = ["lastYear", "currentYear"]
    try:
      for indexYear in range(2):
        query = f"SELECT id, name FROM ref_actor_{indexYear}"
        ManageFromOldDatabase.cursor.execute(query)
        for (id, name) in ManageFromOldDatabase.cursor:
          existAgent = Agent.objects.filter(name__iexact=name, currentYear=indexYear == 1)
          if not existAgent.exists():
            Agent.objects.create(name=name, currentYear=indexYear == 1)
          if not listYear[indexYear] in self.dictAgent:
            self.dictAgent[listYear[indexYear]] = {}
          self.dictAgent[listYear[indexYear]][id] = name
    except db.Error as e:
      return "Error getAgent" + repr(e)
    return ("Agent", False)

  def getAgentFinitions(self):
    try:
      for indexYear in range(2):
        query = "SELECT id, name FROM ref_finition_1"
        ManageFromOldDatabase.cursor.execute(query)
        for (id, name) in ManageFromOldDatabase.cursor:
          existsAgent = AgentFinitions.objects.filter(name__iexact=name, currentYear=indexYear==1)
          if not existsAgent.exists():
            AgentFinitions.objects.create(name=name, currentYear=indexYear==1)
          self.dictAgentFinitions[id] = name
    except db.Error as e:
      return "Error getAgentFinitions" + repr(e)
    return ("AgentFinitions", False)

  def getEnsemble(self):
    listYear = ["lastYear", "currentYear"]
    IndexEnsemble = self.fieldsPdv.index("ensemble")
    for indexYear in range(2):
      dicoEnsemble = {}
      for line in self.listPdv[listYear[indexYear]]:
        nameEnsemble = line[IndexEnsemble]
        if not nameEnsemble in dicoEnsemble:
          dicoEnsemble.append(nameEnsemble)
          Ensemble.objects.create(name=nameEnsemble, currentYear=indexYear==1)
    return ("Ensemble", False)

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
    listYear = ["lastYear", "currentYear"]
    dico = [[], []]
    for indexYear in range(2):
      IndexField = self.fieldsPdv.index(field)
      dico[indexYear] = ['Not assigned']
      classObject.objects.create(name='Not assigned', currentYear=indexYear==1)
      for line in self.listPdv[listYear[indexYear]]:
        nameField = line[IndexField]
        if not nameField in dico[indexYear]:
          dico[indexYear].append(nameField)
          classObject.objects.create(name=nameField, currentYear=indexYear==1)
    return (classObject.__name__, False)

  def getObject(self, nature:str):
    listYear = ["lastYear", "currentYear"]
    try:
      for indexYear in range(2):
        query = f"SELECT id, name FROM ref_{nature}_{indexYear}"
        ManageFromOldDatabase.cursor.execute(query)
        for (id, name) in self.computeHoldingOrder(ManageFromOldDatabase.cursor, nature):
          name, currentYear = self.unProtect(name), listYear[indexYear] == "currentYear"
          kwargs = {"name__iexact":name, "currentYear":currentYear} if getattr(self.typeObject[nature], "currentYear", False) else {"name__iexact":name}
          existobject = self.typeObject[nature].objects.filter(**kwargs)
          if not existobject.exists():
            kwargs = {"name":name, "currentYear":currentYear} if getattr(self.typeObject[nature], "currentYear", False) else {"name":name}
            self.typeObject[nature].objects.create(**kwargs)
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
    for geoOrTrade in geoOrTradeList:
      levelRoot = "root" if geoOrTrade == "geo" else "rootTrade"
      object = TreeNavigation.objects.create(geoOrTrade=geoOrTrade, level=levelRoot, name="France")
      for level, name in self.createNavigationLevelName(geoOrTrade):
        object = TreeNavigation.objects.create(geoOrTrade=geoOrTrade, level=level, name=name, father=object)
      dashboardsLevel = self.createDashboards(geoOrTrade)
      for level, listDashBoard in dashboardsLevel.items():
        levelObject = TreeNavigation.objects.filter(geoOrTrade=geoOrTrade, level=level)
        if levelObject.exists():
          dashboards = [Dashboard.objects.get(name=name) for name in listDashBoard]
          object = DashboardTree.objects.create(geoOrTrade=geoOrTrade, profile=levelRoot, level=levelObject.first())
          for dashboard in dashboards:
            object.dashboards.add(dashboard)
        else:
          return (False, f"Error getTreeNavigation {level} does not exist")
    return ("TreeNavigation", False)

  def createNavigationLevelName(self, geoOrTrade:str):
    geoTreeStructure = json.loads(os.getenv('GEO_TREE_STRUCTURE')) if geoOrTrade == "geo" else json.loads(os.getenv('TRADE_TREE_STRUCTURE'))
    fields, listLevelName = Pdv._meta.fields, []
    for fieldId in geoTreeStructure:
      listLevelName.append((fields[fieldId + 1].name, fields[fieldId + 1].verbose_name))
    return listLevelName

#Création des tableaux de bord
  def createDashboards(self, geoOrTrade):
    if geoOrTrade == "geo":
      CreateWidgetParam.initialize()
    for name, value in CreateWidgetParam.dashboards[geoOrTrade].items():
      layoutName, comment = value[0], value[1]
      comment = json.dumps(comment if isinstance(comment, list) else [comment])
      object = Dashboard.objects.create(name=name, layout=CreateWidgetParam.dictLayout[layoutName], comment=comment)
      templateFlat = []
      for listPos in json.loads(CreateWidgetParam.dictLayout[layoutName].template):
        templateFlat += listPos
      listWidgetParam = CreateWidgetParam.create(name)
      for widgetParam in listWidgetParam[:len(set(templateFlat))]:
        object.widgetParams.add(widgetParam)
    return CreateWidgetParam.dashboardsLevel[geoOrTrade]

# Chargement de la table des ventes
  def getVentes(self):
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
              industry = Industrie.objects.filter(name=industry).first()
              product = self.dictProduct[line[3]]
              product = Produit.objects.filter(name=product).first()
              dateEvent = None
              cy = indexYear == 1
              if line[0]:
                dateEvent = datetime.datetime.fromtimestamp(line[0], tz=tz.gettz("Europe/Paris"))
              Ventes.objects.create(date=dateEvent, pdv=pdv, industry=industry, product=product, volume=float(line[4]), currentYear=cy)

    except db.Error as e:
      return (False, f"Error getVentes {type} {repr(e)}")
    return ("Ventes", False)


# Chargement de la table des utilisateurs

  def getUsers(self):
    dictUser = self.__computeListUser()
    for user in User.objects.all():
      user.groups.clear()
      if not Group.objects.filter(name="root"):
        Group.objects.create(name="root")
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

    data, table, listUser = {"drv":{}, "actor":{}}, {"drv":{}, "actor":{}}, {}
    for field in data.keys():
      query = f'SELECT `id`, `name` FROM `ref_{field}_0`;'
      ManageFromOldDatabase.cursor.execute(query)
      data[field] = {line[0]:line[1] for line in ManageFromOldDatabase.cursor}
      newField = field if field == "drv" else "agent"
      for oldId, value in data[field].items():
        newObject = self.typeObject[newField].objects.filter(name=value, currentYear=True).first()
        if newObject:
          table[field][oldId] = newObject.id
      table[newField] = table[field]
    del table["actor"]

    dictEquiv = {"All":"root", "DRV":"drv", "Secteur":"agent", "Finition":"finition"}
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

# Chargement de la table des ventes
  def getCiblage(self):
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
          kwargs['redistributed'] = line[2] == "does not exist"
          kwargs['sale'] = line[3] == "does not exist"
          kwargs['targetP2CD'] = float(line[4]) if float(line[4]) else 0.0
          kwargs['targetFinition'] = line[5] == "yes"
          kwargs['greenLight'] = line[6][0]
          kwargs['commentTargetP2CD'] = line[7]
          Ciblage.objects.create(**kwargs)

    except db.Error as e:
      return (False, f"Error getCiblage {repr(e)}")
    return ("Ciblage", False)

  def getCiblageLevel(self):
    volP2CD, dnP2CD, volFinition, dnFinition = 1000.0, 50, 150, 30
    dictAgent, now = {}, timezone.now()
    listDrv = {drv.id:drv for drv in Drv.objects.filter(currentYear=True)}
    for drv in listDrv.values():
      dictAgent[drv.id] = set([pdv.agent for pdv in Pdv.objects.filter(sale=True, currentYear=True, drv=drv)])
    for drvId, listAgent in dictAgent.items():
      drv = listDrv[drvId]
      CiblageLevel.objects.create(date=now, drv=drv, volP2CD=volP2CD, dnP2CD=dnP2CD, volFinition=volFinition, dnFinition=dnFinition)
      dvP2CD = volP2CD / len(listAgent)
      ddP2CD, rdP2CD = dnP2CD // len(listAgent), dnP2CD % len(listAgent)
      dvFinition = volFinition / len(listAgent)
      ddFinition, rdFinition = dnFinition // len(listAgent), dnFinition % len(listAgent)
      flagStart = True
      for agent in listAgent:
        if flagStart:
          flagStart = False
          CiblageLevel.objects.create(date=now, agent=agent, volP2CD=dvP2CD, dnP2CD=ddP2CD + rdP2CD, volFinition=dvFinition, dnFinition=ddFinition + rdFinition)
        else:
          CiblageLevel.objects.create(date=now, agent=agent, volP2CD=dvP2CD, dnP2CD=ddP2CD, volFinition=dvFinition, dnFinition=ddFinition)
    return ("CiblageLevel", False)

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
    ParamVisio.objects.create(field="referentielVersion", prettyPrint="Référentiel Version", fvalue="1.0.0", typeValue="str")
    ParamVisio.objects.create(field="softwareVersion", prettyPrint="Logiciel Version", fvalue="4.0.0", typeValue="str")
    ParamVisio.objects.create(field="coeffGreenLight", prettyPrint="Coefficiant feu tricolore", fvalue="2", typeValue="float")
    ParamVisio.objects.create(field="ratioPlaqueFinition", prettyPrint="Ratio Plaque Enduit", fvalue="0.360", typeValue="float")
    ParamVisio.objects.create(field="ratioCustomerProspect", prettyPrint="Ratio Client Prospect", fvalue="0.1", typeValue="float")
    ParamVisio.objects.create(field="currentYear", prettyPrint="Année Courante", fvalue="2021", typeValue="int")
    ParamVisio.objects.create(field="isAdOpen", prettyPrint="Ouverture de l'AD", fvalue="True", typeValue="bool")
    ParamVisio.objects.create(field="delayBetweenUpdates", prettyPrint="Délai entre deux mise à jour", fvalue="10.0", typeValue="float")
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
    # listModel = [DashboardTree, TreeNavigation, WidgetParams, WidgetCompute, Widget, Dashboard, Layout, AxisForGraph, LabelForGraph]
    # for model in listModel:
    #   for element in model.objects.all():
    #     element.delete()
    print("start")
    # manageFromOldDatabase.getTreeNavigation(["geo", "trade"])
    print("end")
    return {"test":False}
    

      



manageFromOldDatabase = ManageFromOldDatabase()