import json, requests, random, math, sys

yn = input("Are you sure you want to run this (y/n)\n> ")
if yn == "n":
    sys.exit("You quit")

with open(r"teamCreation\secrets.json") as json_file:
    fileContents = json.load(json_file)
authKey = fileContents["authKey"]

with open(r"teamCreation\slack_tokens.json") as tokenFile:
    fileContents = json.load(tokenFile)
token = fileContents["actual_token"]

with open(r"teamCreation\slackIDs.json") as idFile:
    userIDs = json.load(idFile)

with open(r"teamCreation\scouters.txt", "r") as scouterList:
    scoutingPairs = scouterList.read().split("\n")

with open(r"teamCreation\inviteToAll.json") as nameFile:
    allInvites = json.load(nameFile)

def getTeams(event="2020ncwak"):
    teams = requests.get(url=f"https://www.thebluealliance.com/api/v3/event/{event}/teams", headers={"X-TBA-Auth-Key": authKey}).json()
    teamList = []
    for team in teams:
        teamList.append(team["key"][3:])
    teamList.remove("5160")
    return teamList

teamList = getTeams()
for i in range(len(teamList)):
    teamList[i] += "_wake_2020"

with open(r"teamCreation\teamsRandomized.json") as readFile:
    scoutsTeams = json.load(readFile)

for i in range(len(teamList)):
    for k, v in scoutsTeams.items():
        if teamList[i] in v:
            botScouters = k
        for person in botScouters.split(", "):
            inviteParams = {"token": token, "channel": teamList[i], "users": userIDs[person]}
            requests.get("https://slack.com/api/conversations.invite", params=inviteParams)

for i in range(len(teamList)):
    for userID in allInvites.values():
        inviteParams = {"token": token, "channel": teamList[i], "users": userIDs[person]}
        requests.get("https://slack.com/api/conversations.invite", params=inviteParams)