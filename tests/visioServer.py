import requests
import json
import time

username, password = "t", "pwd"
address = 'http://localhost:8000'
# address = 'https://visio.fantasiapp.tech:3438'
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
response = requests.get(url, headers=headers, params={"action":"dashboard"})
print(response.headers)
try:
    data = json.loads(response.text)
except:
    data = response.text
print(f"Durée : {time.time() - start} s")
if isinstance(data, dict):
    keys = list(data.keys())
    print("Résultats", keys)
    fields = [
        'structureLevel', 'levelGeo', 'levelTrade', 'structureDashboard', 'indexesDashboard', 'dashboards', 'structureLayout', 'layout', 'widget',
        'structureWidgetParam', 'widgetParams', 'structureWidgetCompute', 'widgetCompute', 'geoTree', 'tradeTree', 'structurePdv', 'indexesPdv', 'pdvs',
        'drv', 'agent', 'dep', 'bassin', 'ville', 'segmentMarketing', 'segmentCommercial', 'enseigne', 'ensemble', 'sousEnsemble', 'site', 'produit',
        'industrie', 'structureTarget', 'target', 'structureTargetLevelDrv', 'targetLevelDrv', 'structureTargetAgentP2CD', 'targetLevelAgentP2CD',
        'structureTargetLevelAgentFinition', 'targetLevelAgentFinition', 'params']
    if len(fields) == len(data):
        for index in range(len(fields)):
            if fields[index] != keys[index]:
                print("pb in fields", fields[index])
    else : print("pb in fields, waited : ", len(fields), "got :", len(data))
else:
    print("pb in data:", data)
# print(data['widgetParams'])

with open(fileName, 'w') as outputFile:
    json.dump(data, outputFile, indent=4)