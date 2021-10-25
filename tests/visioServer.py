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

    try:
        data = json.loads(response.text)
    except:
        print("pb")
    print("post", data)
elif get == "post":
    post = {
        "targetLevelAgentP2CD": {},
        "targetLevelAgentFinitions": {},
        "targetLevelDrv": {},
        "pdvs": {
                "448":[
                    "689109","POINT P - CLIC AULNAY",3,31,3,56,72,372,48.9478,2.47359,7,3,2,22,140,286,True,True,True,True,False,False,None,0,
                    [1632385563,True,True,True,800002,False,"g","",""],
                    [[None,1,1,50929.2],[None,1,3,124.8],[1611689089,3,1,701250],[1611689089,3,2,108000],[1611689089,3,3,155000],[1611689089,3,4,280000],[1611689089,3,5,595000]]]
                },
        "logs":[]
        }
    response = requests.post(url, headers=headers, json=post)
    try:
        data = json.loads(response.text)
    except:
        data = response.text
    print("post", data)

print(f"Durée : {time.time() - start} s")

with open(fileName, 'w') as outputFile:
    json.dump(data, outputFile, indent=4)