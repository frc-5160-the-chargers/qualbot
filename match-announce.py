import tbapy
import discord
import json

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


def generate_match_embed(event, matchnum, year=2019):
    event_id = f"{year}{event}"
    for m in tba_client.event_matches(event_id, simple=True):
        if m["comp_level"] == "qm" and m["match_number"] == matchnum:
            match = m
            break

    teams_blue = match["alliances"]["blue"]["team_keys"]
    teams_red = match["alliances"]["red"]["team_keys"]

    embed=discord.Embed(title=f"Match {matchnum}", color=0x1200ec)
    # embed.set_author(name="Queuing Lady")
    embed.add_field(name="Event", value=f"{event}", inline=False)
    embed.add_field(name="Red Alliance", value=format_team_data(event_id, teams_red), inline=True)
    embed.add_field(name="Blue Alliance", value=format_team_data(event_id, teams_blue), inline=True)
    embed.set_footer(text="Maintained by @Valis#7360")

    return embed

webhook = discord.Webhook.partial(queuing_lady_config["id"], queuing_lady_config["token"], adapter=discord.RequestsWebhookAdapter())
# generate_match_embed("ncwak", 1)
webhook.send(embed=generate_match_embed("ncwak", 1))