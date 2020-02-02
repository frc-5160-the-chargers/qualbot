import tbapy
import discord
import json

from hooks.hook import DiscordHook, SlackHook
from common.slack import create_slack_embed
from common.tba import *

# TODO proper documentation for configuration and deployment
# TODO conglomerate following classes if possible

def get_unplayed_from_config(tba_client: tbapy.TBA, config_data):
    return get_next_unplayed(
        tba_client,
        config_data["event-data"]["name"],
        year=config_data["event-data"]["year"],
        comp_level=config_data["event-data"]["match-type"],
        return_first=config_data["debugging-matches"])

class MatchAnnouncementHookDiscord(DiscordHook):
    def __init__(self, hook_name="queuing-lady-discord", config_file="config.json"):
        super().__init__(hook_name, config_file)
        self.tba_client = tbapy.TBA(self.config_data["tba"])

    def format_match_embed(self, match_data):
        if match_data == None:
            self.logger.warning("Expected match data when formatting embed")
            return
        event_id = match_data["event_key"]
        embed = discord.Embed(title="Match {}".format(match_data['match_number']), color=0x1200ec)
        
        get_alliance_keys = lambda match, alliance: match_data["alliances"][alliance]["team_keys"]
        teams_red = get_alliance_keys(match_data, "red")
        teams_blue = get_alliance_keys(match_data, "blue")

        embed.add_field(name="Red Alliance", value=format_alliance(self.tba_client, event_id, teams_red), inline=True)
        embed.add_field(name="Blue Alliance", value=format_alliance(self.tba_client, event_id, teams_blue), inline=True)
        embed.set_footer(text="Maintained by @Valis#7360")

        return embed

    def generate_embed(self):
        match_data = get_unplayed_from_config(self.tba_client, self.config_data)
        return self.format_match_embed(match_data)

class MatchAnnouncementHookSlack(SlackHook):
    def __init__(self, hook_name="queuing-lady-slack", config_file="config.json"):
        super().__init__(hook_name, config_file)
        self.tba_client = tbapy.TBA(self.config_data["tba"])

    def format_match_embed(self, match_data):
        if match_data == None:
            self.logger.warning("Expected match data when formatting embed")
            return
        
        get_alliance_keys = lambda match, alliance: match_data["alliances"][alliance]["team_keys"]
        teams_red = get_alliance_keys(match_data, "red")
        teams_blue = get_alliance_keys(match_data, "blue")

        event_id = match_data["event_key"]
        embed = {}
        
        embed['text'] = "Upcoming Match!\n<https://www.thebluealliance.com/match/{0}_{1}{2}|Match {2}>".format(event_id, self.config_data["event-data"]["match-type"], match_data['match_number'])
        
        embed['attachments'] = []
        embed['attachments'].append({
            "fallback": "Red Alliance",
            "title": "Red Alliance",
            "color": "#dd0000",
            "text": format_alliance(self.tba_client, event_id, teams_red)
        })
        embed['attachments'].append({
            "fallback": "Blue Alliance",
            "title": "Blue Alliance",
            "color": "#140eb5",
            "text": format_alliance(self.tba_client, event_id, teams_blue)
        })

        return embed

    def generate_embed(self):
        match_data = get_unplayed_from_config(self.tba_client, self.config_data)
        return self.format_match_embed(match_data)