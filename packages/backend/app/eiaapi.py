import requests
import apikey
import json

api_key = apikey.key

url = "https://api.eia.gov/v2/electricity/rto/daily-region-data/data/?frequency=daily&data[0]=value&facets[respondent][]=EPE&facets[type][]=D&facets[type][]=NG&facets[type][]=TI&start=2024-03-01&end=2025-02-12&sort[0][column]=value&sort[0][direction]=desc&offset=0&length=5000&api_key="
url = url + api_key
response = requests.get(url)
# print(response.content)
if response.status_code == 200:
        data = response.json()
        data = data['response']['data']
        # print(json.dumps(data,indent=4))
        for entry in data:
                if entry['period'] == "2024-11-02" and entry['timezone'] == "Mountain":
                        if entry['type'] == "TI":
                                print(f"\tTotal interchange of {entry['value']}")
                        elif entry['type'] == "D":
                                print(f"\tDemand: {entry['value']}")
                        elif entry['type'] == "NG":
                                print(f"\tTotal Net Generated: {entry['value']}")
