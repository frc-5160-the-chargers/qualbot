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

teamList = getTeams()
for i in range(len(teamList)):
    teamList[i] += "_wake_2020"

for i in range(len(teamList)):
    #These lines work, I would not recommend running them until they are needed
    channelParams = {"token": token, "name": teamList[i]}
    requests.get(url="https://slack.com/api/conversations.create", params=channelParams)

teams = randomizeTeams(teamList, len(scoutingPairs))
scoutsTeams = {}
for i in range(len(scoutingPairs)):
    scoutsTeams.setdefault(scoutingPairs[i], teams[i])
with open(r"teamCreation\teamsRandomized.json", "w") as writeFile:
    writeFile.write(str(scoutsTeams))

for i in range(len(teamList)):
    for k, v in scoutsTeams.items():
        if teamList[i] in v:
            botScouters = k
    chatParams = {"token": token, "channel": teamList[i], "text": f"""Hi there, this is the channel for team #{teamList[i]}. If you are a scouter, please remember, qualitative data is a lot more useful to us than quantitative stuff. For example, this teams driver kept crashing into the wall is far more useful than this team climbed in 12 seconds. A scouting report might look something like this:
Qualifier #
Teams on alliance
Observations during autonomous (did it drive across the line, did it not move at all, did it score balls in high / low goal)
Observations during teleop (human controlled) (did the driver go fast, did robot break, good shooter / ball dumper, fast / slow cycles)
Observations during endgame (did they climb, how fast did they climb, reliability of climber)
In general, just get a good vibe with the teams you are scouting, and not feel obligated to takes notes on every single match, if there are 4 robots to scout in a single match, you can probably skip a few if you feel you cant make worthwhile notes.
On the TBA (The Blue Alliance) app, you can star teams that you are scouting and it will notify you when they are about to play.
This team is scouted by {botScouters}"""}
    requests.get(url="https://slack.com/api/chat.postMessage", params=chatParams)

chatParams = {"token": token, "channel": "scouting", "text": f"Scout teams: {scoutsTeams}"}
requests.get(url="https://slack.com/api/chat.postMessage", params=chatParams)