import json, requests, random, math, xlsxwriter

with open(r"teamCreation\secrets.json") as json_file:
    fileContents = json.load(json_file)
authKey = fileContents["authKey"]

with open(r"teamCreation\slack_tokens.json") as tokenFile:
    fileContents = json.load(tokenFile)
token = fileContents["bot_token"]

with open(r"teamCreation\scouters.txt", "r") as scouterList:
    scoutingPairs = scouterList.read().split("\n")

def getTeams(event="2020ncwak"):
    teams = requests.get(url=f"https://www.thebluealliance.com/api/v3/event/{event}/teams", headers={"X-TBA-Auth-Key": authKey}).json()
    teamList = []
    for team in teams:
        teamList.append(team["key"][3:])
    teamList.remove("5160")
    return teamList

def randomizeTeams(teamList, scoutpairs=6):
    random.shuffle(teamList)
    teamRandom = []
    teamsPerPair = math.ceil(len(teamList) / scoutpairs)
    for i in range(0, len(teamList), teamsPerPair):
        teamRandom.append(teamList[i:i + teamsPerPair])
    if len(teamRandom[-1]) != teamsPerPair:
        randomChoice = random.choice(teamRandom[-2])
        teamRandom[-2].remove(randomChoice)
        teamRandom[-1].append(randomChoice)
    return teamRandom

#wb = xlsxwriter.Workbook("teamInfo.xlsx")
#ws = wb.add_worksheet()
teamList = getTeams()
for i in range(len(teamList)):
    #These lines work, I would not recommend running them until they are needed
    #params = {"token": token, "name": teamList[i]}
    #requests.get(url="https://slack.com/api/conversations.create", params=params)
    #ws.write(0, i + 1, teamList[i])
    pass
#wb.close()
params = {"token": token, "channels": "general", "file": "docs\queuing-lady.png"}
r = requests.post("https://slack.com/api/files.upload")
print(r.text)
teams = randomizeTeams(teamList, len(scoutingPairs))
scoutsTeams = {}
for i in range(len(scoutingPairs)):
    scoutsTeams.setdefault(scoutingPairs[i], teams[i])
with open(r"teamCreation\teamsRandomized.txt", "w") as writeFile:
    writeFile.write(str(scoutsTeams))