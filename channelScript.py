import json, requests, random, math

with open("secrets.json") as json_file:
    fileContents = json.load(json_file)

authKey = fileContents["authKey"]
scoutingPairs = ["Aarav Gupta, Aidan Sher, Allen Shen", "Ashleigh Smith, Brandon Yi, Colin Frazer", 
                 "Cy Reading, Harrison Truscott, Jono Jenkens", "Kaeshev Alapati, Max Li, Obinna Modilim",
                 "Ravi Dev, Rin Mauney, Sebastian Polge", "Tommy Frank, Zach Wiebe"]

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
teams = randomizeTeams(teamList)
scoutsTeams = {}
for i in range(len(scoutingPairs)):
    scoutsTeams.setdefault(scoutingPairs[i], teams[i])
with open("teamsRandomized.txt", "w") as writeFile:
    writeFile.write(str(scoutsTeams))