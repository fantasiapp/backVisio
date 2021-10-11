import requests
import json
import time

username, password = "vivian", "pwd"
# address = 'http://localhost:8000'
address = 'https://visio.fantasiapp.tech:3441'
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
if True:
    response = requests.get(url, headers=headers, params={"action":"dashboard"})
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
else:
    response = requests.get(url, headers=headers, params={"action":"update", "nature":"request"})
    # response = requests.post(url, headers=headers, params={"action":"update"}, data={"pdvs":json.dumps({"foo":"bar"})})

    try:
        data = json.loads(response.text)
    except:
        print("pb")

print(f"Durée : {time.time() - start} s")

with open(fileName, 'w') as outputFile:
    json.dump(data, outputFile, indent=4)