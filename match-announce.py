import tbapy
import discord
import json
import random

# TODO fit all of this code into a class or something
# TODO proper documentation for configuration and deployment

# load in data and things like that
with open("config.json", 'r') as f:
    data = json.load(f)
    queuing_lady_config = data["webhooks"]["queuing-lady"]
    tba_config = data["tba"]

tba_client = tbapy.TBA(tba_config["key"])

def format_team_data(event_id, team_ids):
    event_oprs = tba_client.event_oprs(event_id)["oprs"]
    oprs = {i: event_oprs[i] for i in team_ids}
    out = ""
    for team in team_ids:
        team_data = tba_client.team(team)
        out += f"* {team_data['nickname']} [{team_data['team_number']}] -- OPR: {int(oprs[team])}\n"
    return out

def get_match_ids(event, year=2019, comp_level="qm"):
    event_id = f"{year}{event}"
    matches = {}
    for m in tba_client.event_matches(event_id, simple=True):
        if m["comp_level"] == comp_level:
            matches[m["match_number"]] = m
    return matches

def generate_match_embed(match):
    if match == None:
        return
    event_id = match["event_key"]
    embed = discord.Embed(title=f"Match {match['match_number']}", color=0x1200ec)

    get_alliance_keys = lambda match, alliance: match["alliances"][alliance]["team_keys"]
    teams_red = get_alliance_keys(match, "red")
    teams_blue = get_alliance_keys(match, "blue")

    # embed.set_author(name="Queuing Lady")
    # embed.add_field(name="Event", value=f"{event_id}", inline=False)
    embed.add_field(name="Red Alliance", value=format_team_data(event_id, teams_red), inline=True)
    embed.add_field(name="Blue Alliance", value=format_team_data(event_id, teams_blue), inline=True)
    embed.set_footer(text="Maintained by @Valis#7360")

    return embed

def get_next_match(event, year=2019, comp_level="qm"):
    matches = get_match_ids(event, year, comp_level)
    for match in [matches[i] for i in range(1, len(matches)+1)]:
        if match["actual_time"] < 1000000000:
            return match
        elif queuing_lady_config["debugging-matches"]:
            # lol
            if random.random() > 0.5:
                return match

def run_next_match_hook(event, year=2019, comp_level="qm"):
    match_data = get_next_match(event, year, comp_level)
    if match_data != None:
        discord_hook = discord.Webhook.partial(queuing_lady_config["id"], queuing_lady_config["token"], adapter=discord.RequestsWebhookAdapter())
        discord_hook.send(embed=generate_match_embed(match_data))
    
if __name__ == "__main__":
    run_next_match_hook("oncne")