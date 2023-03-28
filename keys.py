import requests
import json

with open(r"discordBot\auth.json") as auth_file:
    authFile = json.load(auth_file)
    authKey = authFile["API"]
year = '2023'

url = f'https://www.thebluealliance.com/api/v3/events/{year}'

headers = {'X-TBA-Auth-Key': authKey}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    events = json.loads(response.text)
    event_keys = [event['key'] for event in events]
else:
    print(f'Request failed with status code {response.status_code}')

with open("keys.txt", 'w') as file:
    json.dump(event_keys, file)