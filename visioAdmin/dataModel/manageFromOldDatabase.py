from dateutil import tz
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
     "ventes":Ventes, "pdv":Pdv, "agent":Agent, "agentfinitions":AgentFinitions, "dep":Dep, "drv":Drv, "bassin":Bassin, "ville":Ville, "segCo":SegmentCommercial,
    "segment":SegmentMarketing, "unused1":Site, "unused2":SousEnsemble, "unused3":Ensemble, "holding":Enseigne,"product":Produit,
    "industry":Industrie, "Tableaux Navigation":DashboardTree, "treeNavigation":TreeNavigation, "Tableaux de Bord":Dashboard, "user":UserProfile,
    "dashBoard":Dashboard, "layout":Layout, "widget":Widget,  "widgetParams":WidgetParams
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
      if not user.username in ["vivian", "jeanluc"]:
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
        ("PdvOld",[]), ("Object", ["drv"]), ("Agent", []), ("Object", ["dep"]), ("Object", ["bassin"]), ("Object", ["holding"]), ("Ensemble", []),
        ("ObjectFromPdv", ["sous-ensemble", SousEnsemble]), ("ObjectFromPdv", ["site", Site]),
        ("Object", ["ville"]), ("Object", ["segCo"]), ("Object", ["segment"]), ("AgentFinitions", []), ("PdvNew", []),
        ("Object", ["product"]), ("Object", ["industry"]), ("Ventes", []), ("TreeNavigation", []), ("Users", [])]
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
      keyValues["closedAt"] = self.__computeClosedAt(line)

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
  def getTreeNavigation(self):
    object = TreeNavigation.objects.create(level="root", name="France")
    for level, name in [("drv", "Région"), ("agent", "Secteur"), ("dep", "Département"), ("bassin", "Bassin")]:
      object = TreeNavigation.objects.create(level=level, name=name, father=object)
    dashboardsLevel = self.createDashboards()
    for level, listDashBoard in dashboardsLevel.items():
      levelObject = TreeNavigation.objects.filter(level=level)
      if levelObject.exists():
        dashboards = [Dashboard.objects.filter(name=name).first() for name in listDashBoard]
        object = DashboardTree.objects.create(profile="root", level=levelObject.first())
        for dashboard in dashboards:
          object.dashboards.add(dashboard)
      else:
        return (False, f"Error getTreeNavigation {level} does not exist")
    return ("TreeNavigation", False)

  def createDashboards(self):
    dashboards = {"Marché P2CD":"column:2:1", "Marché Enduit":"column:2:1", "PdM P2CD":"column:2:1", "PdM Enduit":"column:2:1",
    "PdM P2CD Simulation":"column:2:1", "PdM Enduit Simulation":"column:2:1", "DN P2CD":"column:2:1", "DN Enduit":"column:2:1",
      "DN P2CD Simulation":"column:2:1", "DN Enduit Simulation":"column:2:1", "Points de Vente P2CD":"column:2:1",
      "Points de Vente Enduit":"column:2:1", "Synthèse P2CD":"column:2:1", "Synthèse Enduit":"column:2:1",
      "Synthèse P2CD Simulation":"column:2:1", "Synthèse Enduit Simulation":"column:2:1", "Suivi AD":"column:2:1",
      "Suivi des Visites":"column:2:1", "Marché P2CD Enseigne":"column:2:1", "Marché Enduit Enseigne":"column:2:1",
      "PdM P2CD Enseigne":"column:2:1", "PdM Enduit Enseigne":"column:2:1"
    }
    dictLayout = self.createLayout()
    dictWidget = self.createWidget()
    for name, layoutName in dashboards.items():
      object = Dashboard.objects.create(name=name, layout=dictLayout[layoutName])
      for widgetParam in self.createWidgetParams(name, dictWidget):
        object.widgetParams.add(widgetParam)
    dashboardsLevel = {"root":["Marché P2CD", "Marché Enduit", "PdM P2CD", "PdM Enduit", "PdM P2CD Simulation", "PdM Enduit Simulation", "DN P2CD", "DN Enduit",
      "DN P2CD Simulation", "DN Enduit Simulation", "Points de Vente P2CD", "Points de Vente Enduit", "Synthèse P2CD", "Synthèse Enduit",
      "Synthèse P2CD Simulation", "Synthèse Enduit Simulation", "Suivi AD", "Suivi des Visites"],
      "drv":["Marché P2CD", "Marché Enduit", "PdM P2CD", "PdM Enduit", "PdM P2CD Simulation", "PdM Enduit Simulation", "DN P2CD", "DN Enduit",
      "DN P2CD Simulation", "DN Enduit Simulation", "Points de Vente P2CD", "Points de Vente Enduit", "Synthèse P2CD", "Suivi des Visites"],
      "agent":["Marché P2CD", "Marché Enduit", "PdM P2CD", "PdM Enduit", "PdM P2CD Simulation", "DN P2CD", "DN Enduit",
      "DN P2CD Simulation", "Points de Vente P2CD", "Points de Vente Enduit"],
      "dep":["Marché P2CD", "Marché Enduit", "PdM P2CD", "PdM Enduit", "PdM P2CD Simulation", "DN P2CD", "DN Enduit",
      "DN P2CD Simulation", "Points de Vente P2CD", "Points de Vente Enduit"],
      "bassin":["Marché P2CD", "Marché Enduit", "PdM P2CD", "PdM Enduit", "PdM P2CD Simulation", "DN P2CD", "DN Enduit",
      "DN P2CD Simulation", "Points de Vente P2CD", "Points de Vente Enduit"]
      }
    return dashboardsLevel

  def createLayout(self):
    dictLayout = {}
    data = {
      "column:2:1":[["1","3"],["2","3"]],
      "mono":[["1"]],
      "row:1:1:1":[["1"],["2"],["3"]],
      "row:1I:1:1I":[["1"],["2"],["3"]],
      "row:2:1":[["1", "2"], ["3", "3"]],
      "row:2:2":[["1","2"], ["3", "4"]]
    }
    for name, jsonLayout in data.items():
      object = Layout.objects.create(name=name, template=json.dumps(jsonLayout))
      dictLayout[name] = object
    return dictLayout

  def createWidget(self):
    dictWidget = {}
    for name in ["pie", "donut", "image"]:
      dictWidget[name] = Widget.objects.create(name=name)
    return dictWidget

  def createWidgetParams(self, name:str, dictWidget:str):
    kwargs = {"title":"image", "subTitle":"", "widget":dictWidget["image"], "kwargs":json.dumps("empty")}
    return [WidgetParams.objects.create(**kwargs)]

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
    for username in ["vivian", "jlw"]:
      user = User.objects.get(username=username)
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

    ManageFromOldDatabase.connection.close()
    self.__addPassword(listUser)
    return listUser

  def __addPassword(self, listUser):
    for user in listUser.values():
      user.append("pwd")

  def test(self):
    return {"values":"Le test est fonctionnel"}


# Utilitaires

  def unProtect(self, string):
    if type(string) == str:
      protectDict = {"@":"<£arobase>", "\n":"<£newLine>", "&":"<£andCommercial>", "'":"<£quote>", "\t":"<£tab>", "\\":"<£backSlash>", "\"":"<£doubleQuote>", ".":"<£dot>", "/":"<£slash>", "?":"<£questionMark>", "`":"<£backQuote>", ";":"<£semicolon>", ",":"<£coma>"}
      for (symbol, protect) in protectDict.items():
        string = string.replace(protect, symbol)
      string = string.replace("  ", " ")
      return string.strip()
    return string



manageFromOldDatabase = ManageFromOldDatabase()