import requests
import json
import time
import sys

username, password = "all", "avisio"
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

tokenUrl = f'{address}/visioServer/api-token-auth/'
headers = {'Content-Type': 'application/json'}
data = json.dumps({"username": username, "password": password})
response = requests.post(tokenUrl, headers=headers, data=data)
dictResponse = json.loads(response.text)
token = dictResponse['token']
print("adresse", address, f"Token : {token}")
headers = {'Authorization': f'Token {token}'}

fileName = 'test.json'
url = f'{address}/visioServer/data/'

start = time.time()
if get == "dashboard":
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
            'structureLevel', 'levelGeo', 'levelTrade', 'structureDashboard', 'indexesDashboard', 'dashboards', 'structureWidgetParam', 'widgetParams',
            'geoTree', 'tradeTree', 'structurePdv', 'structureTarget', 'indexesPdv', 'pdvs', 'agent', 'dep', 'bassin', 'ville', 'segmentMarketing', 'segmentCommercial',
            'enseigne', 'ensemble', 'sousEnsemble', 'site', 'produit', 'industrie', 'structureTargetAgentP2CD',
            'targetLevelAgentP2CD', 'structureLayout', 'layout', 'widget', 'structureWidgetcompute', 'widgetCompute', 'structureLabelforgraph',
            'labelForGraph', 'structureAxisforgraph', 'indexesAxisforgraph', 'axisForGraph', 'params']
        if len(fields) == len(data):
            for index in range(len(fields)):
                if fields[index] != keys[index]:
                    print("pb in fields", fields[index])
        else : print("pb in fields, waited : ", len(fields), "got :", len(data))
    else:
        print("pb in data:", data)
elif get == "request" or get == "acknowledge":
    response = requests.get(url, headers=headers, params={"action":"update", "nature":get})
    # response = requests.post(url, headers=headers, params={"action":"update"}, data={"pdvs":json.dumps({"foo":"bar"})})

    try:
        data = json.loads(response.text)
    except:
        print("pb")
elif get == "post":
    response = requests.post(url, headers=headers, json={
        "targetLevelAgentP2CD": {},
        "targetLevelAgentFinition": {},
        "targetLevelDrv": {"10": [1000, 50, 150, 30]},
        "pdvs": {"7207": ["702739", "VM MATERIAUX CHÂTEAU-D'OLONNE",11,42,155,483,1363,46.4925,-1.72913,30,8,25,136,516,1638,
            True,True,True,True,True,True,None,0,False,[[1613420553.0,3,1,70000.0]]]},
        "logs":[]
        })
    try:
        data = json.loads(response.text)
    except:
        data = response.text
    print(data)

print(f"Durée : {time.time() - start} s")

with open(fileName, 'w') as outputFile:
    json.dump(data, outputFile, indent=4)