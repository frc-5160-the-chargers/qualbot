import tbapy
import discord
import json

from .hook import Hook
from tba import *

# TODO proper documentation for configuration and deployment

class MatchAnnouncementHook(Hook):
    def __init__(self, hook_name="queuing-lady", config_file="config.json"):
        super().__init__(hook_name, config_file)
        self.tba_client = tbapy.TBA(self.config_data["tba"])
    
    def format_alliance(self, event_id, team_ids):
        '''format alliance team data into something reasonable to look at'''
        event_oprs = self.tba_client.event_oprs(event_id)["oprs"]
        oprs = {i: event_oprs[i] for i in team_ids}
        out = ""
        for team in team_ids:
            team_data = self.tba_client.team(team, simple=True)
            out += f"* {team_data['nickname']} [{team_data['team_number']}] -- OPR: {round(oprs[team])}\n"
        return out

    def format_match_embed(self, match_data):
        if match_data == None:
            self.logger.warning("Expected match data when formatting embed")
            return
        event_id = match_data["event_key"]
        embed = discord.Embed(title=f"Match {match_data['match_number']}", color=0x1200ec)
        
        get_alliance_keys = lambda match, alliance: match_data["alliances"][alliance]["team_keys"]
        teams_red = get_alliance_keys(match_data, "red")
        teams_blue = get_alliance_keys(match_data, "blue")

        embed.add_field(name="Red Alliance", value=self.format_alliance(event_id, teams_red), inline=True)
        embed.add_field(name="Blue Alliance", value=self.format_alliance(event_id, teams_blue), inline=True)
        embed.set_footer(text="Maintained by @Valis#7360")

        return embed

    def generate_embed(self):
        match_data = get_next_unplayed(
            self.tba_client,
            self.config_data["event-data"]["name"],
            year=self.config_data["event-data"]["year"],
            comp_level=self.config_data["event-data"]["match-type"],
            return_first=self.config_data["debugging-matches"])
        return self.format_match_embed(match_data)

if __name__ == "__main__":
    queuing_lady = MatchAnnouncementHook()
    queuing_lady.send()