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

for i in range(len(teamList)):
    # These lines work, I would not recommend running them until they are needed
    channelList = requests.get("https://slack.com/api/conversations.list", params={"token": token, "exclude_archived": "true"}).json()
    print(channelList["channels"][i]["name"])
    if "wake_2020" in channelList["channels"][i]["name"]:
        channelParams = {"token": token, "channel": channelList["channels"][i]["id"]}
        requests.get("https://slack.com/api/conversations.archive", params=channelParams)