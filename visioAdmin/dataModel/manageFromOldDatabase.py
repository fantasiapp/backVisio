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
  listPdv = []
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
        ("PdvOld",[]), ("ParamVisio", []), ("Object", ["drv"]), ("Agent", []), ("Object", ["dep"]), ("Object", ["bassin"]), ("Object", ["holding"]), ("Ensemble", []),
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
      try:
        query = "SHOW COLUMNS FROM ref_pdv_1"
        ManageFromOldDatabase.cursor.execute(query)
        self.fieldsPdv = [field[0] for field in ManageFromOldDatabase.cursor]
      except db.Error as e:
        return (False, "getPdvOld for fields " + repr(e))

      try:
        query = "SELECT * FROM ref_pdv_1 WHERE `Closed_by_OM` <> 'y'"
        ManageFromOldDatabase.cursor.execute(query)
        for line in ManageFromOldDatabase.cursor:
          line = [self.unProtect(item) for item in line]
          self.listPdv.append(line)
      except db.Error as e:
        return (False, "getPdvOld for values " + repr(e))
    return (False, False)

  def getPdvNew(self):
    for line in self.listPdv:
      keyValues = {}
      keyValues["drv"] = self.__findObject("id_drv", self.dictDrv, line, Drv)
      keyValues["agent"] = self.__findObject("id_actor", self.dictAgent, line, Agent)
      keyValues["dep"] = self.__findObject("id_dep", self.dictDep, line, Dep)
      keyValues["bassin"] = self.__findObject("id_bassin", self.dictBassin, line, Bassin)
      keyValues["ville"] = self.__findObject("id_ville", self.dictVille, line, Ville)
      ensemble = Ensemble.objects.filter(name__iexact=line[self.fieldsPdv.index("ensemble")]).first()
      keyValues["enseigne"] = ensemble.enseigne
      keyValues["ensemble"] = ensemble
      keyValues["sousEnsemble"] = SousEnsemble.objects.filter(name__iexact=line[self.fieldsPdv.index("sous-ensemble")]).first()
      keyValues["site"] = Site.objects.filter(name__iexact=line[self.fieldsPdv.index("site")]).first()
      keyValues["segmentCommercial"] = self.__findObject("id_segCo", self.dictSegco, line, SegmentCommercial)
      keyValues["segmentMarketing"] = self.__findObject("id_segment", self.dictSegment, line, SegmentMarketing)
      keyValues["code"] = line[self.fieldsPdv.index("PDV code")] if line[self.fieldsPdv.index("PDV code")] else None
      keyValues["name"] = line[self.fieldsPdv.index("PDV")] if line[self.fieldsPdv.index("PDV")] else None
      keyValues["latitude"] = line[self.fieldsPdv.index("latitude")] if line[self.fieldsPdv.index("PDV code")] else None
      keyValues["longitude"] = line[self.fieldsPdv.index("longitude")] if line[self.fieldsPdv.index("PDV")] else None
      keyValues["available"] = self.__computeBoolean(line, field="does_not_exist", valueIfNotExist="y")
      keyValues["sale"] = self.__computeBoolean(line, field="sale", valueIfNotExist="y")
      keyValues["redistributed"] = self.__computeBoolean(line, field="redistributed", valueIfNotExist="y")
      keyValues["redistributedEnduit"] = self.__computeBoolean(line, field="redistributedEnduit", valueIfNotExist="y")
      keyValues["pointFeu"] = self.__computeBoolean(line, field="pointFeu", valueIfNotExist="O", inverse=True)
      # keyValues["closedAt"] = 0 #self.__computeClosedAt(line)

      for field, object in keyValues.items():
        if object == None and field != "closedAt":
          return [False, "field {}, Pdv {}, code {} does not exists".format(field, keyValues["name"], keyValues["code"])]
      existsPdv = Pdv.objects.filter(code=keyValues["code"])
      if not existsPdv.exists():
        Pdv.objects.create(**keyValues)
      else:
        return (False, "Pdv {}, code {} already exists".format(keyValues["name"], keyValues["code"]))
    return ("Pdv", False)

  def __computeBoolean(self, line:list, field:str, valueIfNotExist:str, inverse:bool=False) -> bool:
    valueFound = line[self.fieldsPdv.index(field)]
    return valueFound == valueIfNotExist if inverse else valueFound != valueIfNotExist

  def __computeClosedAt(self, line:list):
    timestamp = line[self.fieldsPdv.index("toBeClosed")]
    if timestamp:
      return datetime.fromtimestamp(timestamp, tz=tz.gettz("Europe/Paris"))
    return None

  def __findObject(self, fieldName, dico, line, model):
    indexObject =  self.fieldsPdv.index(fieldName)
    idObject = line[indexObject]
    nameObject =dico[idObject] if idObject in dico else dico[1]
    objectFound = model.objects.filter(name=nameObject)
    return objectFound.first() if objectFound.exists() else None

  def getAgent(self):
    try:
      query = "SELECT id, name FROM ref_actor_1"
      ManageFromOldDatabase.cursor.execute(query)
      drvCorrespondance = self.__getDrvCorrespondance()
      for (id, name) in ManageFromOldDatabase.cursor:
        existAgent = Agent.objects.filter(name__iexact=name)
        if not existAgent.exists():
          idDrv = drvCorrespondance[id]
          nameDrv = self.dictDrv[idDrv]
          drv = Drv.objects.filter(name=nameDrv)
          if drv.exists():
            Agent.objects.create(name=name, drv=drv.first())
          else:
            return (False, "Agent {} has no drv".format(name))
        self.dictAgent[id] = name
    except db.Error as e:
      return "Error getAgent" + repr(e)
    return ("Agent", False)

  def getAgentFinitions(self):
    try:
      query = "SELECT id, name, id_drv FROM ref_finition_1"
      ManageFromOldDatabase.cursor.execute(query)
      for (id, name, id_drv) in ManageFromOldDatabase.cursor:
        existsAgent = AgentFinitions.objects.filter(name__iexact=name)
        if not existsAgent.exists():
          nameDrv = self.dictDrv[id_drv]
          drv = Drv.objects.filter(name=nameDrv)
          if drv.exists():
            Agent.objects.create(name=name, drv=drv.first())
          else:
            return (False, "AgentFinitions {} has no drv".format(name))
        self.dictAgentFinitions[id] = name
    except db.Error as e:
      return "Error getAgentFinitions" + repr(e)
    return ("AgentFinitions", False)

  def __getDrvCorrespondance(self):
    IndexAgent = self.fieldsPdv.index("id_actor")
    IndexDrv =  self.fieldsPdv.index("id_drv")
    drvCorrespondance = {}
    for line in self.listPdv:
      idAgent = line[IndexAgent]
      if not idAgent in drvCorrespondance:
        drvCorrespondance[idAgent] = line[IndexDrv]
    return drvCorrespondance

  def getEnsemble(self):
    IndexEnsemble = self.fieldsPdv.index("ensemble")
    IndexEnseigne = self.fieldsPdv.index("id_holding")
    dicoEnsemble, dicoEnseigne = {}, {}
    for line in self.listPdv:
      nameEnsemble = line[IndexEnsemble]
      idEnseigneOld = self.__cleanEnseigne(line[IndexEnseigne], nameEnsemble)
      nameEnseigne = self.dictHolding[idEnseigneOld]
      if not nameEnseigne in dicoEnsemble:
        dicoEnsemble[nameEnseigne] = []
      if not nameEnsemble in dicoEnsemble[nameEnseigne]:
        dicoEnsemble[nameEnseigne].append(nameEnsemble)
        if not nameEnseigne in dicoEnseigne:
          existsObject = Enseigne.objects.filter(name__iexact=nameEnseigne)
          if existsObject.exists:
            dicoEnseigne[nameEnseigne] = existsObject.first()
          else:
            return (False, "Error getEnsemble : Enseigne {} does not exist".format(nameEnseigne))
        Ensemble.objects.create(name=nameEnsemble, enseigne=dicoEnseigne[nameEnseigne])
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
    IndexField = self.fieldsPdv.index(field)
    dico = ['Not assigned']
    classObject.objects.create(name='Not assigned')
    for line in self.listPdv:
      nameField = line[IndexField]
      if not nameField in dico:
        dico.append(nameField)
        classObject.objects.create(name=nameField)
    return (classObject.__name__, False)

  def getObject(self, type:str):
    try:
      query = f"SELECT id, name FROM ref_{type}_1"
      ManageFromOldDatabase.cursor.execute(query)
      for (id, name) in ManageFromOldDatabase.cursor:
        name = self.unProtect(name)
        existobject = self.typeObject[type].objects.filter(name__iexact=name)
        if not existobject.exists():
          self.typeObject[type].objects.create(name=name)
        dict = getattr(self, "dict" + type.capitalize())
        dict[id] = name
    except db.Error as e:
      return (False, f"Error getObject {type} {repr(e)}")
    return (type, False)

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
    dictPdv = {line[0]:line for line in self.listPdv}
    indexCode = self.fieldsPdv.index("PDV code")
    try:
      query = "SELECT timestamp, id_pdv, id_industry, id_product, volume FROM data_ad_1"
      ManageFromOldDatabase.cursor.execute(query)
      for line in ManageFromOldDatabase.cursor:
          if line[4] != 0.0 and line[1] in dictPdv:
            idOld = line[1]
            code = dictPdv[idOld][indexCode]
            pdv = Pdv.objects.filter(code=code).first()
            industry = self.dictIndustry[line[2]]
            industry = Industrie.objects.filter(name=industry).first()
            product = self.dictProduct[line[3]]
            product = Produit.objects.filter(name=product).first()
            dateEvent = None
            if line[0]:
              dateEvent = datetime.fromtimestamp(line[0], tz=tz.gettz("Europe/Paris"))
            Ventes.objects.create(date=dateEvent, pdv=pdv, industry=industry, product=product, volume=float(line[4]))

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
    for username, userList in dictUser.items():
      user = User.objects.create_user(username=username, password=userList[2])
      groupName = userList[0]
      if not Group.objects.filter(name=groupName):
        Group.objects.create(name=groupName)
      user.groups.add(Group.objects.get(name=groupName))
      if int(userList[1]):
        UserProfile.objects.create(user=user, idGeo=int(userList[1]))
    return ("Users", False)

  def __computeListUser(self):
    query = "SELECT `userPseudo`, `profile` FROM user;"
    dictUser = {}
    ManageFromOldDatabase.cursor.execute(query)
    for line in ManageFromOldDatabase.cursor:
      dictUser[line[0]] = line[1]

    data, table, listUser = {"drv":{}, "actor":{}}, {"drv":{}, "actor":{}}, {}
    for field in data.keys():
      query = f'SELECT `id`, `name` FROM `ref_{field}_0`;'
      ManageFromOldDatabase.cursor.execute(query)
      data[field] = {line[0]:line[1] for line in ManageFromOldDatabase.cursor}
      newField = field if field == "drv" else "agent"
      for oldId, value in data[field].items():
        newObject = self.typeObject[newField].objects.filter(name=value).first()
        if newObject:
          table[field][oldId] = newObject.id
      table[newField] = table[field]
    del table["actor"]
    dictEquiv = {"All":"root", "DRV":"drv", "Secteur":"agent", "Finition":"finition"}
    for pseudo, profile in dictUser.items():
      listProfile = list(profile.split(":"))
      typeTable = dictEquiv[listProfile[0]]
      oldId = int(listProfile[2])
      listData = [typeTable, table[typeTable][oldId] if typeTable in table and oldId in table[typeTable] else 0]
      listUser[pseudo] = listData
    self.__addPassword(listUser)
    return listUser

  def __addPassword(self, listUser):
    for user in listUser.values():
      user.append("pwd")

# Chargement de la table des ventes
  def getCiblage(self):
    dictPdv = {line[0]:line for line in self.listPdv}
    indexCode = self.fieldsPdv.index("PDV code")
    try:
      query = "SELECT timestamp, id_pdv, depot, sale, targetVolume, targetFinition, greenLight, commentTarget FROM ciblage;"
      ManageFromOldDatabase.cursor.execute(query)
      for line in ManageFromOldDatabase.cursor:
        idOld = line[1]
        if idOld in dictPdv:
          kwargs = {}
          kwargs['date'] = datetime.fromtimestamp(line[0], tz=tz.gettz("Europe/Paris")) if line[0] else None
          code = dictPdv[idOld][indexCode]
          kwargs['pdv'] = Pdv.objects.filter(code=code).first()
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
    for agent in Agent.objects.all():
      drv = agent.drv
      if not drv in dictAgent:
        dictAgent[drv] = [agent]
      else:
        dictAgent[drv].append(agent)
    for drv, listAgent in dictAgent.items():
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
      pdv = Pdv.objects.filter(code=line[0])
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
    print(Layout.listFields())
    print(Layout.listIndexes())
    print(Layout.dictValues())
    print("end")
    return {"test":False}
      



manageFromOldDatabase = ManageFromOldDatabase()