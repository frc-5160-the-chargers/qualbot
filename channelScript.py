import json, requests, random

with open("secrets.json") as json_file:
    fileContents = json.load(json_file)

authKey = fileContents["authKey"]

def getTeams(event="2020ncwak"):
    teams = requests.get(url=f"https://www.thebluealliance.com/api/v3/event/{event}/teams", headers={"X-TBA-Auth-Key": authKey}).json()
    teamList = []
    for team in teams:
        teamList.append(team["key"][3:])
    return teamList

def randomizeTeams(teamList, scoutpairs=9):
    random.shuffle(teamList)
    teamsPerPair = int(len(teamList) / scoutpairs)

print(getTeams())