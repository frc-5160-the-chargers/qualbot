import discord
import json
import logging
import re
import os

token_file="bot_token.json"
with open(token_file) as f:
    client_token = json.load(f)['token'];


unarchive_category_name = 'team_scouting';
archive_category_name = 'scouting_archive';

currentFilepath = 'currentEvent.json';
pastFilepath = 'pastEvents.json';
infoFilepath = 'events/{0}/eventInfo.json';
guildFilePath = 'guildInfo.json';

command_character = '!';

scoutingbot_data = None;

MENTION_REGEX = "/^<@!?(\d+)>$/"

channels_purpose_noscouters = 'Record qualitative data about each team, and check pins (or scroll up) for interview data. Team {0} is currently not scouted by anyone. Use ' + f'{command_character}scouters add [@user] [team] in #scouting to add a scouter.'
channels_purpose_scouters = 'Record qualitative data about each team, and check pins (or scroll up) for interview data. Team {0} is scouted by: ';


team_QInfo_header_msg = 'Quantiative data section for team {0}:';
team_QInfo_header_msg_name = 'header'; #Note: special name for the header message in the quantitative data section; do not name any qInfo data header.
team_QInfo_structure = {
    'can_climb':{'message':'Can It Climb???','reactions':{'✅':'Yes','❌':'No'}}
    
    
};


class Bot:
    def __init__(self,client):
        self.currentEvent = {};
        self.currentEventInfo = {};
        self.past_events = [];
        self.guild_data = {};
        self.client = client;
        self.loadData();
        print(self.currentEvent);
        print(self.currentEventInfo);
        print(self.past_events);
        

    def emptyEventInfo(self):
        return {'teams':[],'scouters':[],'teamScouters':{},'scouterTeams':{},'teamChannels':{},'name':'','teamQMessages':{},'qInfoStructure':team_QInfo_structure};

    def getMentions(self,text):
        mentionObjects = re.findall(MENTION_REGEX,text);
        mentions = [obj for obj in mentionObjects];
        return mentions;

    def isMention(self,text):
        return (re.match(MENTION_REGEX,text) is not None);


    #takes a discord emoji id or a unicode emoji name, which can be used in add_reaction
    def getEmojiFromID(self,emoji):
        emoji_obj = self.client.get_emoji(emoji);
        if (emoji_obj is None):
            return emoji;
        return emoji_obj;

        
    def saveData(self):
        with open(pastFilepath,'w') as pastFile:
            json.dump(self.past_events,pastFile);
        with open(guildFilePath,'w') as guildFile:
            json.dump(self.guild_data,guildFile);
        with open(currentFilepath,'w') as currentFile:
            json.dump(self.currentEvent,currentFile);
        print(self.currentEvent);
        if (self.inEvent()):
            with open(infoFilepath.format(self.currentEvent['name']),'w') as infoFile:
                json.dump(self.currentEventInfo,infoFile);

    def loadData(self):
        try:
            with open(pastFilepath,'r') as pastFile:
                self.past_events = json.load(pastFile);
        except:
            self.past_events = [];

        try:
            with open(guildFilePath,'r') as guildFile:
                self.guild_data = json.load(guildFile);
        except:
            self.guild_data = {};
        
        try:
            with open(currentFilepath,'r') as currentFile:
                self.currentEvent = json.load(currentFile);
        except:
            self.currentEvent = {};
        
        try:
            if (self.inEvent()):
                with open(infoFilepath.format(self.currentEvent['name']),'r') as infoFile:
                    self.currentEventInfo = json.load(infoFile);
            else:
                self.currentEventInfo = {};
        except:
            self.currentEventInfo = {};

    def startEvent(self,name):
        if (not(self.inEvent())):
            if (name in self.past_events):
                return f'Error: event name already used. Try making the name unique by adding the year. If you want to open an already created event, use {command_character}event open [name].'
            self.currentEventInfo = self.emptyEventInfo();
            self.currentEventInfo['name'] = name;
            self.currentEvent = {'name':name,'filepath':name};
            print(self.currentEvent);
            if (not(os.path.isdir(f'events/{name}/'))):
                os.mkdir(f'events/{name}/');
            self.saveData();
            return f'Event {name} successfully created! \nUse {command_character}event teams set [team1] [team2] [...] to register the teams in the event, and {command_character}event end to end the event.';
        else:
            return f'Error: already an event in session. Please use {command_character}event end to end the current event.';

    async def endEvent(self,guild,sourceChannel):
        if (not(self.inEvent())):
            return f'Error: no event in session. Please use {command_character}event start [name] to start an event';
        else:
            if (self.currentEvent['name'] not in self.past_events):
                self.past_events.append(self.currentEvent['name']);
            await sourceChannel.send(content="Archiving event channels...");
            archive_category = None;
            if ('archive_category_id' not in self.guild_data or self.guild_data['archive_category_id'] is None):
                archive_category = await guild.create_category(archive_category_name);
                self.guild_data['archive_category_id'] = archive_category.id;
            else:
                archive_category = guild.get_channel(self.guild_data['archive_category_id'])
                
            for channel_id in self.currentEventInfo['teamChannels'].values():
                channel = guild.get_channel(channel_id);
                if (channel is not None and channel.category_id is not archive_category.id):
                    await channel.edit(category=archive_category);
                    
            self.saveData();
            self.currentEvent = {};
            self.saveData();
            self.currentEventInfo = {};
            return f'Event successfully ended! To reopen a previous event, use {command_character}event open [name], and to start a new one, use {command_character}event start [name]';

    def getPreviousEvents(self):
        return 'Previous events: ' + ', '.join(self.past_events) + f'.\nTo reopen one of these, use {command_character}event open [name]';

            
    async def openEvent(self,guild,name,sourceChannel):
        if (self.inEvent()):
            return f'Error: already an event in session. Please use {command_character}event end to end the current event.';
        elif (not name in self.past_events):
            return f'Error: no event named {name} in the archived past events. Use {command_character}event previous to see previous events.';
        else:
            self.currentEvent = {'name':name,'filepath':name};
            fp = open(infoFilepath.format(name));
            self.currentEventInfo = json.load(fp);
            print('opening event');
            unarchive_category = None;
            print(self.guild_data);
            await sourceChannel.send(content="Unarchiving event channels...");
            if ('unarchive_category_id' not in self.guild_data or self.guild_data['unarchive_category_id'] is None):
                print('not in');
                unarchive_category = await guild.create_category(unarchive_category_name);
                self.guild_data['unarchive_category_id'] = unarchive_category.id;
            else:
                unarchive_category = guild.get_channel(self.guild_data['unarchive_category_id']);
                
            for channel_id in self.currentEventInfo['teamChannels'].values():
                channel = guild.get_channel(channel_id)
                if (channel is not None and channel.category_id is not unarchive_category.id):
                    await channel.edit(category=unarchive_category,sync_permissions=True);
            self.saveData();
            return f'Event successfully reopened!';
        
    async def setTeams(self,teams,guild,sourceChannel):
        if (not self.inEvent()):
            return f'Error: no event in session. Please use {command_character}event start [name] to start an event';
        else:
            await sourceChannel.send(content="Creating team channels...");
            self.currentEventInfo['teams'] = list(set(teams));
            self.currentEventInfo['teams'].sort();
            await self.createChannels(guild);
            self.saveData();
            return f'Event teams set. To view the teams in the event, use {command_character}event teams.';

    def eventInfo(self):
        if(self.inEvent()):
            name = self.currentEvent['name'];
            teamsCount = str(len(self.currentEventInfo['teams']) if len(self.currentEventInfo['teams']) > 0 else 'None');
            scoutersCount = str(len(self.currentEventInfo['scouters']) if len(self.currentEventInfo['scouters']) > 0 else 'None');
            return f'Current event: {name}\nNumber of teams: {teamsCount}\nNumber of scouters: {scoutersCount}';
        else:
            return f'Error: no event in session. Please use {command_character}event start [name] to start an event';


    def teamsList(self):
        if (self.inEvent()):
            teamList = ', '.join(self.currentEventInfo["teams"]);
            return f'teams in the current event: {teamList}';
        else:
            return f'Error: no event in session. Please use {command_character}event start [name] to start an event';
            
    def getScouterTeams(self,user,username):
        if (not self.inEvent()):
            return f'Error: no event in session. Please use {command_character}event start [name] to start an event';
        elif (user in self.currentEventInfo['scouters'] and len(self.currentEventInfo['scouterTeams'][user]) > 0):
            teams = self.currentEventInfo['scouterTeams'][user];
            teamLinks = ['<#{0}>'.format(self.currentEventInfo['teamChannels'][team]) for team in teams];
            joinedTeamList = ', '.join(['{0} - {1}'.format(team,teamLink) for (team,teamLink) in zip(teams,teamLinks)]);
            return f'Scouter {username} is currently scouting teams: {joinedTeamList}';
        else:
            return f'Error: {username} not registered as scouting any teams. Please use {command_character}scouters add @[user] [team number] to register a scouter.'

    async def getTeamScouters(self,guild,team):
        if (not self.inEvent()):
            return f'Error: no event in session. Please use {command_character}event start [name] to start an event';
        elif (team not in self.currentEventInfo['teams']):
            return f'Error: team {team} not in the current event\'s teams list. Please use {command_character}event teams set [team1] [team2] [..] to set the teams';
        elif (team in self.currentEventInfo['teamScouters'] and len(self.currentEventInfo['teamScouters'][team]) > 0):
            usernames = ', '.join([await self.getUsername(guild,user) for user in self.currentEventInfo['teamScouters'][team]]);
            channel_id = self.currentEventInfo['teamChannels'][team];
            teamChannel = f'<#{channel_id}>';
            return f'Users scouting team {team} (channel: {teamChannel}): {usernames}';
        else:
            return f'Error: team not currently scouted by any users. If this team should be scouted, please use {command_character}scouters add [@user1] [@user2] [..] [team number 1] [team number 2] [...] to register a scouter(s) of that team.';

    async def listScouters(self,guild):
        if (not self.inEvent()):
            return f'Error: no event in session. Please use {command_character}event start [name] to start an event';
        else:
            usernames = [await self.getUsername(guild,user) for user in self.currentEventInfo['scouters']];
            return f'List of users currently scouting teams: {", ".join(usernames)}';

    async def addScouter(self,guild,users,teams):
        if (not self.inEvent()):
            return f'Error: no event in session. Please use {command_character}event start [name] to start an event';
        else:
            print(users);
            bad_teams = [];
            good_teams = [];
            for team in teams:
                if (team in list(set(self.currentEventInfo['teams']))):
                    good_teams.append(team);
                else:
                    bad_teams.append(team);
            print(bad_teams);
            teams = list(set(good_teams));
            users = list(set(users));
            
            for team in teams:
                if (team not in self.currentEventInfo['teamScouters']):
                    self.currentEventInfo['teamScouters'][team] = list(set(users));
                else:
                    self.currentEventInfo['teamScouters'][team] = list(set(users) | set(self.currentEventInfo['teamScouters'][team]));
                    
            for user in users:
                
                if (user not in self.currentEventInfo['scouterTeams']):
                    self.currentEventInfo['scouterTeams'][user] = list(set(teams));
                else:
                    self.currentEventInfo['scouterTeams'][user] = list(set(teams) | set(self.currentEventInfo['scouterTeams'][user]));
            
                if (user not in self.currentEventInfo['scouters']):
                    self.currentEventInfo['scouters'].append(user);
            
            [await self.updateChannels(guild,team=team) for team in teams];

            self.saveData();

            username_list = ', '.join([await self.getUsername(guild,user) for user in users]);
            teams_list = ', '.join(teams);
            bad_teams_error = '';
            if (len(bad_teams) > 0):
                bad_teams_error = 'Error: teams ' + ', '.join(bad_teams) + f' not registered in current event. Please use {command_character}event teams set [team1] [team2] [...] to set the teams.\n'
            return bad_teams_error + f'Scouters {username_list} now scouting teams {teams_list}. \nPlease use {command_character}scouters get [team|@user] to see who\'s scouting whom and get team channel links.'

    async def removeScouter(self,guild,users,teams):
        if (not self.inEvent()):
            return f'Error: no event in session. Please use {command_character}event start [name] to start an event';
        else:
            print(users);
            bad_teams = [];
            good_teams = [];
            for team in teams:
                if (team in self.currentEventInfo['teams']):
                    good_teams.append(team);
                else:
                    bad_teams.append(team);
            teams = list(set(good_teams));
            users = list(set(users));
            
            for team in teams:
                if (team not in self.currentEventInfo['teamScouters']):
                    self.currentEventInfo['teamScouters'][team] = [];
                else:
                    self.currentEventInfo['teamScouters'][team] = list(set(self.currentEventInfo['teamScouters'][team]) - set(users));
                    
            for user in users:
                
                if (user not in self.currentEventInfo['scouterTeams']):
                    self.currentEventInfo['scouterTeams'][user] = [];
                else:
                    self.currentEventInfo['scouterTeams'][user] = list(set(self.currentEventInfo['scouterTeams'][user]) - set(teams));
            
                if (user not in self.currentEventInfo['scouters']):
                    self.currentEventInfo['scouters'].append(user);
            
            [await self.updateChannels(guild,team) for team in teams];

            self.saveData();

            username_list = ', '.join([await self.getUsername(guild,user) for user in users]);
            teams_list = ', '.join(teams);
            bad_teams_error = '';
            if (len(bad_teams) > 0):
                bad_teams_error = 'Error: teams ' + ', '.join(bad_teams) + f' not registered in current event. Please use {command_character}event teams set [team1] [team2] [...] to set the teams.\n'
            return bad_teams_error + f'Scouters {username_list} no longer scouting teams {teams_list}. \nPlease use {command_character}scouters get [team|@user] to see who\'s scouting whom and get team channel links.'


    #called indirectly, returns object of reactionCounts
    async def fetchQuantitativeDataCounts(self,guild,team,dataName):
            qInfoStruct = self.currentEventInfo['qInfoStructure'];
            chosenQData = qInfoStruct[dataName];
            message = await (guild.get_channel(self.currentEventInfo['teamChannels'][team])).fetch_message(self.currentEventInfo['teamQMessages'][team][dataName]);
            return self.getReactionCounts(message,list(chosenQData['reactions'].keys()));
            

    async def getQuantitativeData(self,guild,team,dataName=None):
        
        if (not self.inEvent()):
            return f'Error: no event in session. Please use {command_character}event start [name] to start an event';
        elif (team not in self.currentEventInfo['teams']):
            return f'Error: team {team} not registered in current event. Please use {command_character}event teams set [team1] [team2] [...] to set the teams at an event';
        elif (dataName is not None and dataName not in self.currentEventInfo['qInfoStructure']):
            return f'Error: quantitative data {dataName} not tracked for the current event. Please use {command_character}event data list to see the quantitative data tracked at this event. If you think some other quantitative data should be tracked, contact harrison truscott or the current maintainer of the scouting bot.';
        else:
            if (dataName is not None):
                reactionCounts = await self.fetchQuantitativeDataCounts(guild,team,dataName);
                chosenQData = self.currentEventInfo['qInfoStructure'][dataName];
                responses = [];
                for (emojiID) in reactionCounts:
                    count = reactionCounts[emojiID];
                    if (count > 1):
                        response = str(chosenQData['reactions'][emojiID]);
                        if count > 2:
                            response += f' (x{count-1})';
                        responses.append(response);
                return f'Team {team}\'s quantitative data, {dataName}: ' + (', '.join(responses) if len(responses) > 0 else 'None') + '.\nTo input quantiative interview data for a team, find the quantitative messages with {command_character}event data link [team] or by going to the team\'s channel and scrolling to the top/checking the pinned messages. React with the appropriate emote to select the option you want.';
            else:
                qInfoStruct = self.currentEventInfo['qInfoStructure'];
                result = f'Team {team}\'s quantitative data:';
                for datum in qInfoStruct.keys():
                    reactionCounts = await self.fetchQuantitativeDataCounts(guild,team,datum);
                    chosenQData = self.currentEventInfo['qInfoStructure'][datum];
                    responses = [];
                    for (emojiID) in reactionCounts:
                        count = reactionCounts[emojiID]
                        if (count > 1):
                            response = str(chosenQData['reactions'][emojiID]);
                            if count > 2:
                                response += f' (x{count-1})';
                            responses.append(response);
                    result += f'\n{datum}: ' + (', '.join(responses) if len(responses) > 0 else 'None');
                result += f'\nTo input quantiative interview data for a team, find the quantitative messages with {command_character}event data link [team] or by going to the team\'s channel and scrolling to the top/checking the pinned messages. React with the appropriate emote to select the option you want.';
                return result;
                    

                    

    def listEventTrackedQData(self):
        if (not self.inEvent()):
            return f'Error: no event in session. Please use {command_character}event start [name] to start an event';
        else:
            tracked_data = list(self.currentEventInfo['qInfoStructure'].keys());
            eventName = self.currentEvent['name']
            return f'Data tracked for event {eventName}: ' + ', '.join(tracked_data);

    async def getTeamQDataLink(self,guild,team):
        if (not self.inEvent()):
            return f'Error: no event in session. Please use {command_character}event start [name] to start an event';
        elif (team not in self.currentEventInfo['teams']):
            return f'Error: team {team} not registered in current event. Please use {command_character}event teams set [team1] [team2] [...] to set the teams at an event';
        else:
            channel = guild.get_channel(self.currentEventInfo['teamChannels']);
            message = await channel.fetch_message(self.currentEventInfo['teamQMessages'][team][team_QInfo_header_msg_name]);
            return f'Team {team} Quantitative Data: ' + message.jump_url + '.';



    def getReactionCounts(self,message,emojiIDList):
        reactions = message.reactions;
        emojiObjList = [self.getEmojiFromID(emoji) for emoji in emojiIDList];
        result = {};
        for reaction in reactions:
            if (reaction.emoji in emojiObjList):
                result[emojiIDList[emojiObjList.index(reaction.emoji)]] = reaction.count;
        return result;
                

        
    async def createQuantitativeMessages(self,channel,team,qInfoStruct):
        self.currentEventInfo['teamQMessages'][team] = {};
        header = await channel.send(content=team_QInfo_header_msg.format(team));
        self.currentEventInfo['teamQMessages'][team][team_QInfo_header_msg_name] = header.id;

        for (qName) in qInfoStruct:
            qMsg = qInfoStruct[qName];
            msg_text = qMsg['message'];
            print(qMsg);
            print(msg_text);
            message = await channel.send(content=msg_text);

            for emojiId in qMsg['reactions']:
                emoji = self.getEmojiFromID(emojiId);
                await message.add_reaction(emoji);
            self.currentEventInfo['teamQMessages'][team][qName] = message.id;
        for msgId in self.currentEventInfo['teamQMessages'][team].values():
            message = await channel.fetch_message(msgId);
            message.pin();

    

    #no conditionals because it should never be called by the user directly; whenever the teams are updated, the channels are created
    async def createChannels(self,guild):
        print('teams creating');
        teamsList = self.currentEventInfo['teams'];
        prefix = self.currentEventInfo['name'] + '-team ';
        qInfo = self.currentEventInfo['qInfoStructure'];
        for team in teamsList:
            if (not (team in self.currentEventInfo['teamChannels'])):
                unarchive_category = None
                if ('unarchive_category_id' not in self.guild_data or self.guild_data['unarchive_category_id'] is None):
                    unarchive_category = await guild.create_category(unarchive_category_name);
                    self.guild_data['unarchive_category_id'] = unarchive_category.id;
                else:
                    unarchive_category = guild.get_channel(self.guild_data['unarchive_category_id'])
                print('adding new team channel');
                channelObject = await guild.create_text_channel(name=prefix+team,category=unarchive_category);
                self.currentEventInfo['teamChannels'][team] = channelObject.id;
                await self.createQuantitativeMessages(channelObject,team,qInfo);
        
        await self.updateChannels(guild);


    async def updateChannels(self,guild,team=None):
        teamsList = [team];
        print('channel updating');
        if (team is None):
            teamsList = self.currentEventInfo['teams'];
        for team in teamsList:
            channelId = self.currentEventInfo['teamChannels'][team];
            channel = guild.get_channel(channelId);
            
            
            correctPurpose = channels_purpose_noscouters.format(team);
            if (team in self.currentEventInfo['teamScouters'] and len(self.currentEventInfo['teamScouters'][team]) > 0):
                correctPurpose = channels_purpose_scouters.format(team) + ', '.join([await self.getUsername(guild,user) for user in self.currentEventInfo['teamScouters'][team]]);
            
            if (channel.topic is not correctPurpose):
                obj = channel.edit(topic=correctPurpose);


    async def getUsername(self,guild,userId):
        user = await guild.get_member(userId);
        if (user is not None):
            return str(user);
        return None;
        
        

    def inEvent(self):
        return not((self.currentEvent is None) or (self.currentEvent == {}));

    async def messageGet(self,message):

        print('bot msg do');
        
        guild = message.guild;


        channel = message.channel
        user = message.author;

        text = message.content;

        mentions = message.mentions; #Not in order, just all existent mentions.

        if (text.startswith(command_character)):
            print('is_command');
            command_args = text[1:].split(' ');
            num_args = len(command_args);
            print(command_args);
            if (command_args[0] == 'help'):
                await channel.send(f'Help for general commands:\n{command_character}event [arguments] - get information about and manage the current event, start or end an event, or open a previous one.\n{command_character}scouters [arguments] - get information about scouters / team scouting in the current event. An event must be open for most {command_character}scouters commands.\nUse {command_character}[command] help to get detailed information about command syntaxes.');
                    
            elif (command_args[0] == 'event'):
                if (num_args == 1):
                    await channel.send(f'Error in command syntax. Please use {command_character}event info to see info on the current event, and {command_character}event help to see a list of the event commands.');

                elif (num_args >= 2 and command_args[1] == 'help'):
                    texts = [f'Help for scouters commands:', f'{command_character}event help - get help for the event commands', f'{command_character}event start [name] - start a new event with the name [name]. There must not be an event in session, and the name must not have been used in any previous events.', f'{command_character}event end - ends the current event and archives the team channels',f'{command_character}event open [name] - opens a previous event [name] and unarchives the team channels. The event functions as normal from that point. [name] must be in the list of previous events per below.',f'{command_character}event previous - displays the list of all previous events. See above.', f'{command_character}event teams - list the teams registered in the current event', f'{command_character}event teams set [team1] [team2] [team3] - set the current teams at the event (and create team channels if there aren\'t already)'];
                    await channel.send('\n'.join(texts));
                    
                elif (num_args >= 2 and command_args[1] == 'start'):
                    return_msg = '';
                    if num_args == 2:
                        return_msg = f'Error in command syntax: please follow format {command_character}event start [event_name]';
                    elif num_args == 3:
                        return_msg = self.startEvent(command_args[2]);
                    else:
                        return_msg = f'Error in command syntax: please do not uses spaces in names - use underscores instead.';
                    if (return_msg is not None and return_msg != ''):
                            await channel.send(return_msg);
                elif (num_args >= 2 and command_args[1] == 'end'):
                    return_msg = await self.endEvent(guild,channel);
                    if (return_msg is not None and return_msg != ''):
                        await channel.send(return_msg);

                elif (num_args >= 2 and command_args[1] == 'previous'):
                    return_msg = self.getPreviousEvents();
                    if (return_msg is not None and return_msg != ''):
                        await channel.send(return_msg);

                elif (num_args >= 2 and command_args[1] == 'info'):
                    return_msg = self.eventInfo();
                    if (return_msg is not None and return_msg != ''):
                        await channel.send(return_msg);
                elif (num_args >= 2 and command_args[1] == 'data'):
                    return_msg = None;
                    if (num_args < 3):
                        return_msg = "error";
                    elif (command_args[2] == 'list'):
                        return_msg = self.listEventTrackedQData();
                    elif (command_args[2] == 'link'):
                        if (num_args < 4):
                            return_msg = 'Error in command syntax: please specify team to generate a link for.';
                        else:
                            return_msg = await self.getTeamQDataLink(guild,command_args[3]);
                    elif (command_args[2] == 'get'):
                        if (num_args < 4):
                            return_msg = 'Error in command syntax: please specify team to get data from.';
                        elif (num_args == 4):
                            return_msg = await self.getQuantitativeData(guild,command_args[3]);
                        else:
                            return_msg = await self.getQuantitativeData(guild,command_args[3],command_args[4]);
                    else:
                        return_msg = "error";
                        
                    if (return_msg is not None and return_msg != ''):
                        await channel.send(return_msg);
                        
                    
                elif (num_args >= 2 and command_args[1] == 'open'):
                    return_msg = None;
                    if (num_args < 3):
                        return_msg = f'Error in command syntax: please specify name of previous event to open';
                    elif (num_args >3):
                        return_msg = f'Error in command syntax: please do not use spaces in names. If an event already happened, its name had no spaces. \nTry underscores, or use {command_character}event previous to get a list of the previous events';
                    else:
                        return_msg = await self.openEvent(guild,command_args[2],channel);
                    if (return_msg is not None and return_msg != ''):
                        await channel.send(return_msg);

                elif (num_args >= 2 and command_args[1] == 'teams'):
                    return_msg = '';
                    if (num_args == 2):
                        return_msg = self.teamsList();
                    
                    elif (num_args > 3 and command_args[2] == 'set'):
                        teams = command_args[3:];
                        return_msg = await self.setTeams(teams,guild,channel);
                    else:
                        remaining_args = ' '.join(command_args[2:]);
                        return_msg = f'Invalid {command_character}event teams arguments: {remaining_args}. Please use {command_character}event help for options.';
                    
                    if (return_msg is not None and return_msg != ''):
                        await channel.send(return_msg);
                else:
                    await channel.send(f'Invalid {command_character}event arguments: {text[7:]}. Please use {command_character}event help to see a list of the event commands.');


            elif (command_args[0] == 'scouters'):
                if (num_args == 1):
                    await channel.send(f'Error in command syntax. Please use {command_character}scouters help to see a list of the scouters commands.');

                elif (num_args >= 2 and command_args[1] == 'help'):
                    texts = [f'Help for scouters commands:', f'{command_character}scouters help - get help for the scouters command', f'{command_character}scouters get [team number | @scouter] - get info on who\'s scouting what team. Also returns links to the team channels', f'{command_character}scouters list - list users scouting teams in the current event', f'{command_character}scouters add [@user1] [@user2] [...] [team number 1] [team number 2] [...] - add scouters scouting teams. Will add the specified teams to each of the users\'s teams lists.', f'{command_character}scouters remove [@user1] [@user2] [...] [team1] [team2] [...] - removes each team from the specified users\' teams lists (if they exist).'];
                    await channel.send('\n'.join(texts));  

                elif (num_args >= 2 and command_args[1] == 'get'):
                    return_msg = None;
                    if (num_args == 2):
                        return_msg = f'Error in command syntax: please specify either a team number or a mention a scouter with syntax {command_character}scouters get [team number | @scouter] \n(remember to mute pings in #scouting if you haven\'t already so you can use mentions';
                    elif self.isMention(command_args[2]):
                        user = await self.getMentions(command_args[2])[0];
                        return_msg = await self.getScouterTeams(user, await self.getUsername(guild,user));
                    else:
                        return_msg = await self.getTeamScouters(guild,command_args[2]);
                    if (return_msg is not None and return_msg != ''):
                        await channel.send(return_msg);

                elif (num_args >= 2 and command_args[1] == 'list'):
                    return_msg = await self.listScouters(guild);
                    if (return_msg is not None and return_msg != ''):
                        await channel.send(return_msg);

                elif (num_args >= 2 and command_args[1] == 'add'):
                    return_msg = None;
                    if (num_args < 4):
                        return_msg = f'Error in command syntax: please specify both the names and teams to add scouters with the syntax {command_character}scouters add @[name1] @[name2] @[name...] [team number 1] [team number 2] [team number ...]';
                    elif (len(mentions) == 0):
                        return_msg = f'Error in command syntax: please specify both the names and teams to add scouters with the syntax {command_character}scouters add @[name1] @[name2] @[name...] [team number 1] [team number 2] [team number ...]';
                    else:
                        non_mention_args = [arg for arg in command_args[2:] if (not(self.isMention(arg)))];
                        return_msg = await self.addScouter(guild,mentions,non_mention_args);
                    if (return_msg is not None and return_msg != ''):
                        await channel.send(return_msg);

                elif (num_args >= 2 and command_args[1] == 'remove'):
                    return_msg = None;
                    if (num_args < 4):
                        return_msg = f'Error in command syntax: please specify both the names and teams to remove scouted teams with the syntax {command_character}scouters remove @[name1] @[name2] @[name...] [team number 1] [team number 2] [team number ...]';
                    elif (len(mentions) == 0):
                        return_msg = f'Error in command syntax: please specify both the names and teams to remove scouted teams with the syntax {command_character}scouters remove @[name1] @[name2] @[name...] [team number 1] [team number 2] [team number ...]';
                    else:
                        non_mention_args = [arg for arg in command_args[2:] if (not(self.isMention(arg)))];
                        return_msg = await self.removeScouter(guild,mentions,non_mention_args);
                    if (return_msg is not None and return_msg != ''):
                        await channel.send(return_msg);
                else:
                    await channel.send(f'Invalid {command_character}scouters arguments: {text[7:]}. Please use {command_character}scouters help to see a list of the event commands.');


            else:
                await channel.send(f'Error in command syntax. Please use {command_character}help to see a list of commands.');
                        


if __name__ == '__main__':
    client = discord.Client();
    bot = Bot(client);

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
   

    if message.author == client.user:
        return
    await bot.messageGet(message);

@client.event
async def on_raw_reaction_add(payload):



    print(f'reaction added by {payload.user_id}, id: {payload.emoji}');

@client.event
async def on_raw_reaction_remove(payload):
    print(f'reaction removed by {payload.user_id}, id: {payload.emoji}');

    

if __name__ == '__main__':
    client.run(client_token);
    

