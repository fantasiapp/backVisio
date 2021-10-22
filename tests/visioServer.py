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

    try:
        data = json.loads(response.text)
    except:
        print("pb")
    print("post", data)
elif get == "post":
    post = {
        "targetLevelAgentP2CD": {81:[200, 10]},
        "targetLevelAgentFinitions": {14:[30, 0]},
        "targetLevelDrv": {9:[7003, 50]},
        "pdvs": {
                "3777":
                ["685658", "POINT P - DOCKS DE L'OISE COMPIEGNE", 9, 71, 10, 149, 468, 83, 49.3922, 2.79104, 25, 8, 24, 71, 468, 1090,
                True, True, True, True, False, False, None, 12,
                [1634385823, True, False, 11111, False, "g", "Ceci est un commentaire de test"],
                [[None, 1, 1, 12408], [None, 1, 2, 8697.6],
                [None, 1, 3, 3262.08], [1611672332, 3, 1, 222222],
                [1611672332, 4, 2, 17425], [1611672332, 11, 3, 37800], [1611672332, 3, 4, 29900],[1611672332, 3, 5, 26350], [1634375855.552321, 6, 1, 100000],
                [1634375855.552321, 6, 2, 100000], [1634375855.552321, 10, 3, 100000], [None, 7, 3, 4000], [None, 10, 4, 2025], [None, 10, 5, 2500],
                [None, 15, 4, 22500], [None, 15, 5, 23500], [None, 18, 3, 4000], [None, 21, 4, 1250]]]
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