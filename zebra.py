import requests
import json

with open(r"discordBot\auth.json") as auth_file:
    authFile = json.load(auth_file)
    authKey = authFile["API"]

with open("keys.txt", 'r') as file:
    event_keys = json.load(file)

for event_key in event_keys:
    url = f'https://www.thebluealliance.com/api/v3/event/{event_key}/matches/simple'

    headers = {'X-TBA-Auth-Key': authKey}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        matches = json.loads(response.text)
        match_keys = [match['key'] for match in matches]
    else:
        print(f'Request failed with status code {response.status_code}')

    if match_keys != []:
        for match_key in match_keys:
            url = f'https://www.thebluealliance.com/api/v3/match/{match_key}/zebra_motionworks'

            headers = {'X-TBA-Auth-Key': authKey}

            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                data = json.loads(response.text)
                if data != None:
                    print(event_key)
                break
            else:
                print(f'Request failed with status code {response.status_code}')