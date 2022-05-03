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
    
    LogAdmin.objects.all().delete()
    self.cursorNew.execute("ALTER TABLE `visioServer_logadmin` AUTO_INCREMENT=1;")
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
    print("start populate", start)
    if start:
      ManageFromOldDatabase.connection = db.connect(
      user = os.getenv('DB_USERNAME'),
      password = os.getenv('DB_PASSWORD'),
      host = os.getenv('DB_HOST'),
      database = os.getenv('DB_NAME_START')
      )
    ManageFromOldDatabase.cursor = ManageFromOldDatabase.connection.cursor()
    self.cursor.execute("Show tables;")
    listTable = [table[0] for table in self.cursor.fetchall()]
    print("listTable", listTable)
    for table in listTable:
      if "visioServer" in table:
        print(table)
        self.connectionNew.execute("TRUNCATE TABLE table_name")

    #   self.dictPopulate = [
    #     ("PdvOld",[]), ("SynonymAdmin",[]), ("ParamVisio", []), ("Object", ["drv"]), ("Agent", []), ("Object", ["dep"]), ("Object", ["bassin"]),
    #     ("Object", ["industry"]), ("Object", ["product"]), ("Object", ["holding"]), ("ObjectFromPdv", ["ensemble", Ensemble]),
    #     ("ObjectFromPdv", ["sous-ensemble", SousEnsemble]), ("ObjectFromPdv", ["site", Site]),
    #     ("Object", ["ville"]), ("Object", ["segCo"]), ("Object", ["segment"]), ("AgentFinitions", []), ("PdvNew", []), ("Users", []),
    #     ("TreeNavigation", [["geo", "trade"]]),
    #     ("Target", []), ("TargetLevel", []), ("Visit", []), ("Sales", [])]
    # if self.dictPopulate:
    #   tableName, variable = self.dictPopulate.pop(0)
    #   print(tableName, variable[0] if  len(variable) > 0 else '')
    #   table, error = getattr(self, "get" + tableName)(*variable)
    #   error = [error] if error else []
    #   message = "L'ancienne base de données est lue" if tableName == "PdvOld" else f"La table {str(table)} est remplie "
    #   return {'query':method, 'message':message, 'end':False, 'errors':error}
    ManageFromOldDatabase.connection.close()
    return {'query':method, 'message':"<b>La base de données a été remplie</b>", 'end':True, 'errors':[]}

# Chargement de la table des utilisateurs
  def getUsers(self):
    dictUser = self.__computeListUser()
    Group.objects.create(name="root")
    for user in User.objects.all():
      user.groups.add(Group.objects.get(name="root"))
      UserProfile.objects.create(user=user, idGeo=0, admin=True)
    for username, userList in dictUser.items():
      user = User.objects.create_user(username=username, password=userList[2])
      groupName = userList[0]
      if not Group.objects.filter(name=groupName):
        Group.objects.create(name=groupName)
      user.groups.add(Group.objects.get(name=groupName))
      UserProfile.objects.create(user=user, idGeo=int(userList[1]) if int(userList[1]) else 0, admin = (user.id == 3))
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
    ParamVisio.objects.create(field="isAdOpenSave", prettyPrint="Ouverture de l'AD base Save", fvalue="True", typeValue="bool")
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