from mzqc import MZQCFile as qc
import json
import requests

url = "https://apps.lifs-tools.org/mzqcvalidator/validator/"
# payload={
#     "data1":1234,'data2':'test'
# }
with open("tests/nameOfYourFile.mzQC", "r") as file:
    payload = qc.JsonSerialisable.from_json(file)
            
headers = {'Content-Type': 'text/plain'}
response = requests.post(url, headers=headers, data=qc.JsonSerialisable.to_json(payload))
print(response.text , response.status_code)


headers = {'Content-Type': 'application/json'}
response = requests.post(url, headers=headers, data=qc.JsonSerialisable.to_json(payload))
print(response.text , response.status_code)
