import re
import json

from Behaviors.Behavior import Behavior

class TeamComment(Behavior):

    def __init__(self, name):
        super().__init__(name)

    def create_json(self, message):
        #get the team number
        match = re.search(r"^\s{0,}\d{1,4} ", message.content)
        matchstr = match.group(0)
        team_number = int(matchstr.strip())
        #get the comment
        team_comment = message.content[match.end(0):]
        #get the commenter ID
        commenter_name = message.author.name
        commenter_id = message.author.id

        print(team_number)
        print(team_comment)
        print(commenter_name)
        print(commenter_id)

        #TODO: Add something to check the TBA/`FIRST API to see if we're at a tournament, then add the tournament to the stored data

        #group stuff into a dict
        comment = {
            "team number": team_number,
            "comment": team_comment,
            "commenter name": commenter_name,
            "commenter id": commenter_id
        }

        return comment

    def check(self, message):
        return re.search(r"^\s{0,}\d{1,4} ", message.content)
    
    def do(self, message):
        """Log comments made by team members. Keep track of team #, comment, and commenter."""

        #for match comments
        if message.channel.id == 614093378749202447:
            with open("Files/match_comments.json", "a") as json_file:
                json.dump(self.create_json(message), json_file, indent=4)
        #for general team comments
        elif message.channel.id == 614093398030286880:
            with open("Files/team_comments.json", "a") as json_file:
                json.dump(self.create_json(message), json_file, indent=4)

