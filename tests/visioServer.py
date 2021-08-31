import requests
import json
import time

username, password = "vivian", "pwd"
address = 'http://localhost:8000'
# address = 'http://work.visio.fantasiapp.tech:2438'
tokenUrl = f'{address}/visioServer/api-token-auth/'
print("Url:", tokenUrl)
headers = {'Content-Type': 'application/json'}
data = json.dumps({"username": username, "password": password})
response = requests.post(tokenUrl, headers=headers, data=data)
dictResponse = json.loads(response.text)
token = dictResponse['token']
print(f"Token : {token}")
headers = {'Authorization': f'Token {token}'}

outputFile = 'test.json'
url = f'{address}/visioServer/data/'

start = time.time()
response = requests.get(url, headers=headers) 
print(f"Durée : {time.time() - start} s")
try:
    data = json.loads(response.text)
except:
    data = response.text

with open(outputFile, 'w') as outputFile:
    json.dump(data, outputFile, indent=4)

response = requests.get(url, headers=headers, params={"action":"navigation"})

try:
    data = json.loads(response.text)
except:
    data = response.text

print(data)

print("Done.")
