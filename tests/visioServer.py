import requests
import json
import time

username, password = "t", "pwd"
# address = 'http://localhost:8000'
address = 'http://visio.fantasiapp.tech:2438'
tokenUrl = f'{address}/visioServer/api-token-auth/'
print("Url:", tokenUrl)
headers = {'Content-Type': 'application/json'}
data = json.dumps({"username": username, "password": password})
response = requests.post(tokenUrl, headers=headers, data=data)
dictResponse = json.loads(response.text)
print(dictResponse)
token = dictResponse['token']
print(f"Token : {token}")
headers = {'Authorization': f'Token {token}'}

fileName = 'test.json'
url = f'{address}/visioServer/data/'

start = time.time()
response = requests.get(url, headers=headers, params={"action":"dashboard"})
# response = requests.get(url, headers=headers, params={"action":"navigation"})

try:
    data = json.loads(response.text)
except:
    data = response.text
print(f"Durée : {time.time() - start} s")
print(data)

with open(fileName, 'w') as outputFile:
    json.dump(data, outputFile, indent=4)
