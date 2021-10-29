import requests
import json
import time
import sys

username, password = "t", "avisio"
address = 'http://localhost:8000'
# address = 'https://visio.fantasiapp.tech:3441'
get = "dashboard"

arguments = sys.argv
if len(arguments) > 1:
    host = arguments[1]
    if host == "local": address = 'http://localhost:8000'
    elif host == "temp": address = 'https://visio.fantasiapp.tech:3441'
    elif host == "work": address = 'https://visio.fantasiapp.tech:3438'
    elif host == "current": address = 'https://visio.fantasiapp.tech:3439'
    elif host == "distrib": address = 'https://visio.fantasiapp.tech:3440'
    elif host == "distrib2": address = 'https://visio.fantasiapp.tech:3442'

if len(arguments) > 2:
    get = arguments[2]

def queryForToken(userName, password):
    tokenUrl = f'{address}/visioServer/api-token-auth/'
    headers = {'Content-Type': 'application/json'}
    data = json.dumps({"username": userName, "password": password})
    response = requests.post(tokenUrl, headers=headers, data=data)
    dictResponse = json.loads(response.text)
    return dictResponse['token']

fileName = 'test.json'
url = f'{address}/visioServer/data/'

start = time.time()
if get == "dashboard":
    token = queryForToken(username, password)
    print("adresse", address, f"Token : {token}")
    headers = {'Authorization': f'Token {token}'}
    response = requests.get(url, headers=headers, params={"action":"dashboard", "blocked":"True"})
    print(response.headers)
    try:
        data = json.loads(response.text)
    except:
        data = response.text

    if isinstance(data, dict):
        keys = list(data.keys())
        print("Résultats", keys)
        fields = [
            'structureLevel', 'levelGeo', 'levelTrade', 'levelGeo_ly', 'levelTrade_ly', 'geoTree', 'tradeTree', 'geoTree_ly', 'tradeTree_ly', 'structureTarget', 'structureSales', 'structurePdvs', 'indexesPdvs', 'pdvs', 'pdvs_ly', 'structureDashboards', 'indexesDashboards', 'dashboards', 'structureLayout', 'layout', 'widget', 'structureWidgetparams', 'indexesWidgetparams', 'widgetParams', 'structureWidgetcompute', 'widgetCompute', 'params', 'structureLabelforgraph', 'labelForGraph', 'structureAxisforgraph', 'indexesAxisforgraph', 'axisForGraph', 'segmentMarketing', 'segmentMarketing_ly', 'segmentCommercial', 'segmentCommercial_ly', 'enseigne', 'enseigne_ly', 'ensemble', 'ensemble_ly', 'sousEnsemble', 'sousEnsemble_ly', 'site', 'site_ly', 'product', 'industry', 'agent', 'agent_ly', 'structureAgentfinitions', 'indexesAgentfinitions', 'agentFinitions', 'agentFinitions_ly', 'dep', 'dep_ly', 'bassin', 'bassin_ly', 'ville', 'structureTargetlevel', 'targetLevelAgentFinitions', 'targetLevelAgentFinitions_ly', 'timestamp'
            ]
        if len(fields) == len(data):
            for index in range(len(fields)):
                if fields[index] != keys[index]:
                    print("pb in fields", fields[index])
        else : print("pb in fields, waited : ", len(fields), "got :", len(data))
        with open(fileName, 'w') as outputFile:
            json.dump(data, outputFile, indent=4)
    else:
        print("pb in data:", data)
elif get == "request" or get == "acknowledge":
    token = queryForToken(username, password)
    headers = {'Content-Type': 'application/json'}
    response = requests.get(url, headers=headers, params={"action":"update", "nature":get})

    try:
        data = json.loads(response.text)
    except:
        print("pb")
    print("request", data)
elif get == "post":
    postNat = {
        'targetLevelAgentP2CD': {},
        'targetLevelAgentFinitions': {'4': [2100, 0], '5': [2100, 0], '3': [3100, 0]},
        'targetLevelDrv': {'2': [10000, 121], '1': [10000, 122]},
        'pdvs': {},
        "logs":[
            [False,True,[],11,None,False,None,None,False],
            [False,True,[],11,None,False,None,None,False],
            [False,True,[],2,None,False,None,None,False],
            [False,True,[],1,None,False,None,None,False],
            [False,True,[],3,None,False,None,None,False]]
        }
    postDrv = {
        'targetLevelAgentP2CD': {'13': [1250, 6], '14': [1250, 6]},
        'targetLevelAgentFinitions': {},
        'targetLevelDrv': {},
        'pdvs': {},
        'logs':[[False,True,[],14,None,False,None,6,False]]
        }
    postP2CD =  {
        "targetLevelAgentP2CD":{},
        "targetLevelAgentFinitions":{},
        "targetLevelDrv":{},
        "pdvs": {"108": [
            "685658","POINT P - DOCKS DE L'OISE COMPIEGNE",3,31,3,55,71,83,49.3922,2.79104,12,3,2,2,63,94,True,True,True,True,False,False,None,0,
            [1635182798.999377,True,True,True,200000,False,"g","test",""],
            [
                [None,1,1,12408],
                [None,1,2,8697.6],
                [None,1,3,3262.08],
                [1611672332,3,1,116450],
                [1611672332,3,2,17425],
                [1611672332,3,3,17800],
                [1611672332,3,4,28900],
                [1611672332,3,5,26350],
                [None,7,3,3000],
                [None,10,4,2025],
                [None,10,5,2500],
                [None,15,4,22500],
                [None,15,5,23500],
                [None,18,3,4000],[None,21,4,1250],[1635238079,6,1,100000],[1635238082,6,2,100000],[1635238086,6,3,100000]]]}
    }
    postFinitions = {
        'targetLevelAgentP2CD': {},
        'targetLevelAgentFinitions': {},
        'targetLevelDrv': {},
        'pdvs': {'183': [
            '686416', 'BRETAGNE MATERIAUX ST GREGOIRE', '5', '30', '2', '46', '106', '149', 48.1358, -1.68935, '16', '3', '2', '34', '55', '150', True, True, True, True, True, False, None, 6,
            [1635237787, True, True, True, 0, 168830, '', '', ''],
            [[1606235629, 3, 1, 360000], [None, 3, 2, 80000], [None, 3, 3, 88000], [None, 3, 4, 100000], [None, 3, 5, 60000], [None, 21, 4, 21250]]]}}

    listPost = [
        {"post":postNat, "user":"all", "pwd":"avisio"},
        {"post":postDrv,"user":"y", "pwd":"avisio"},
        {"post":postP2CD,"user":"t", "pwd":"avisio"},
        {"post":postFinitions,"user":"ribiere", "pwd":"ovisio"}
    ]

    for credentials in listPost:
        token = queryForToken(credentials["user"], credentials["pwd"])
        headers = {'Authorization': f'Token {token}'}
        response = requests.post(url, headers=headers, json=credentials["post"])

        try:
            data = json.loads(response.text)
            if "error" in data:
                print("error", credentials["user"])
                print("data", credentials["post"])
                break
            else:
                print("OK", credentials["user"])
        except:
            data = response.text

print(f"Durée : {time.time() - start} s")