import os
import time
import re
import slack
import logging
import json
import datetime
import nest_asyncio
nest_asyncio.apply()

tokens_file = "slack_tokens.json";
with open(tokens_file) as f:
    tokens = json.load(f);
    slack_token = tokens["bot_token"];
    app_token = tokens["app_token"];




scoutingbot_data = None;
scoutingbot_id = '';

command_character = '!';

RTM_READ_DELAY = 1;
EXAMPLE_COMMAND = "do";
MENTION_REGEX = "<@(|[WU].+?)>"

currentFilepath = 'currentEvent.json';
pastFilepath = 'pastEvents.json';
infoFilepath = 'events\\{0}\\eventInfo.json';

channels_topic = 'scouting';
channels_purpose_noscouters = 'Record qualitative data about each team. Each scouter scouting this team should take/post notes here so others can see. Team {0} is currently not scouted by anyone. Use ' + f'{command_character}scouters add [@user] [team] in #scouting to add a scouter.'
channels_purpose_scouters = 'Record qualitative data about each team. Each scouter scouting this team should take/post notes here so others can see. Team {0} is scouted by: ';

    
class bot:
    


    # message json example: {"channel":"C061EG9SL","text":"I hope the tour went well, Mr. Wonka.","attachments":[{"text":"Who wins the lifetime supply of chocolate?","fallback":"You could be telling the computer exactly what it can do with a lifetime supply of chocolate.","color":"#3AA3E3","attachment_type":"default","callback_id":"select_simple_1234","actions":[{"name":"winners_list","text":"Who should win?","type":"select","data_source":"users"}]}]}

    
    def __init__(self):
        self.currentEvent = {};
        self.currentEventInfo = {};
        self.past_events = [];
        self.loadData();

        self.appClient = slack.WebClient(token=app_token);
        
        print(self.currentEvent);
        print(self.currentEventInfo);
        print(self.past_events);
        print(self.appClient.auth_test());
        

    def emptyEventInfo(self):
        return {'teams':[],'scouters':[],'teamScouters':{},'scouterTeams':{},'teamChannels':{},'name':''}

    def getMentions(self,text):
        mentionObjects = re.findall(MENTION_REGEX,text);
        mentions = [obj for obj in mentionObjects];
        return mentions;

    def isMention(self,text):
        return (re.match(MENTION_REGEX,text) is not None);
        

    ##def getUnusedFilepath(ideal_name):
    ##    if (not ideal_name in self.past_events):
    ##        return ideal_name;
    ##    current_year = datetime.datetime.now().year;
    ##    if (not f'{ideal_name}_{current_year}' in self.past_events):
    ##        return f'{ideal_name}_{current_year}';
    ##    

    def saveData(self):
        with open(pastFilepath,'w') as pastFile:
            json.dump(self.past_events,pastFile);
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
            if (not(os.path.isdir(f'events\\{name}\\'))):
                os.mkdir(f'events\\{name}\\');
            self.saveData();
            return f'Event {name} successfully created! \nUse {command_character}event teams set [team1] [team2] [...] to register the teams in the event, and {command_character}event end to end the event.';
        else:
            return f'Error: already an event in session. Please use {command_character}event end to end the current event.';

    def endEvent(self):
        if (not(self.inEvent())):
            return f'Error: no event in session. Please use {command_character}event start [name] to start an event';
        else:
            if (self.currentEvent['name'] not in self.past_events):
                self.past_events.append(self.currentEvent['name']);
            for channel in self.currentEventInfo['teamChannels'].values():
                obj = self.appClient.channels_info(channel=channel);
                if (obj['ok'] and not(obj['channel']['is_archived'])):
                    self.appClient.channels_archive(channel=channel);
            self.saveData();
            self.currentEvent = {};
            self.saveData();
            self.currentEventInfo = {};
            return f'Event successfully ended! To reopen a previous event, use {command_character}event open [name], and to start a new one, use {command_character}event start [name]';

    def getPreviousEvents(self):
        return 'Previous events: ' + ', '.join(self.past_events) + f'.\nTo reopen one of these, use {command_character}event open [name]';

            
    def openEvent(self,name):
        if (self.inEvent()):
            return f'Error: already an event in session. Please use {command_character}event end to end the current event.';
        elif (not name in self.past_events):
            return f'Error: no event named {name} in the archived past events. Use {command_character}event previous to see previous events.';
        else:
            self.currentEvent = {'name':name,'filepath':name};
            fp = open(infoFilepath.format(name));
            self.currentEventInfo = json.load(fp);
            print('opening event');
            for channel in self.currentEventInfo['teamChannels'].values():
                obj = self.appClient.channels_info(channel=channel);
                if (obj['ok'] and (obj['channel']['is_archived'])):
                    self.appClient.channels_unarchive(channel=channel);
            self.saveData();
            return f'Event successfully reopened!';
        
    def setTeams(self,teams):
        if (not self.inEvent()):
            return f'Error: no event in session. Please use {command_character}event start [name] to start an event';
        else:
            self.currentEventInfo['teams'] = teams;
            self.createChannels();
            self.saveData();
            return f'Event teams set. To view the teams in the event, use {command_character}event teams.';

    def eventInfo(self):
        if(self.inEvent()):
            name = self.currentEvent['name'];
            return f'Current event: {name}';
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

    def getTeamScouters(self,team):
        if (not self.inEvent()):
            return f'Error: no event in session. Please use {command_character}event start [name] to start an event';
        elif (team not in self.currentEventInfo['teams']):
            return f'Error: team {team} not in the current event\'s teams list. Please use {command_character}event teams set [team1] [team2] [..] to set the teams';
        elif (team in self.currentEventInfo['teamScouters'] and len(self.currentEventInfo['teamScouters'][team]) > 0):
            usernames = ', '.join([self.getUsername(user) for user in self.currentEventInfo['teamScouters'][team]]);
            return f'Users scouting team {team}: {usernames}';
        else:
            return f'Error: team not currently scouted by any users. If this team should be scouted, please use {command_character}scouters add [@user1] [@user2] [..] [team number 1] [team number 2] [...] to register a scouter(s) of that team.';

    def listScouters(self):
        if (not self.inEvent()):
            return f'Error: no event in session. Please use {command_character}event start [name] to start an event';
        else:
            usernames = [self.getUsername(user) for user in self.currentEventInfo['scouters']];
            return f'List of users currently scouting teams: {", ".join(usernames)}';

    def addScouter(self,users,teams):
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
            
            [self.updateChannels(team) for team in teams];

            self.saveData();

            username_list = ', '.join([self.getUsername(user) for user in users]);
            teams_list = ', '.join(teams);
            bad_teams_error = '';
            if (len(bad_teams) > 0):
                bad_teams_error = 'Error: teams ' + ', '.join(bad_teams) + f' not registered in current event. Please use {command_character}event teams set [team1] [team2] [...] to set the teams.\n'
            return bad_teams_error + f'Scouters {username_list} now scouting teams {teams_list}. \nPlease use {command_character}scouters get [team|@user] to see who\'s scouting whom and get team channel links.'

    def removeScouter(self,users,teams):
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
            
            [self.updateChannels(team) for team in teams];

            self.saveData();

            username_list = ', '.join([self.getUsername(user) for user in users]);
            teams_list = ', '.join(teams);
            bad_teams_error = '';
            if (len(bad_teams) > 0):
                bad_teams_error = 'Error: teams ' + ', '.join(bad_teams) + f' not registered in current event. Please use {command_character}event teams set [team1] [team2] [...] to set the teams.\n'
            return bad_teams_error + f'Scouters {username_list} no longer scouting teams {teams_list}. \nPlease use {command_character}scouters get [team|@user] to see who\'s scouting whom and get team channel links.'

    #no conditionals because it should never be called by the user directly; whenever the teams are updated, the channels are created
    def createChannels(self):
        print('teams creating');
        teamsList = self.currentEventInfo['teams'];
        prefix = self.currentEventInfo['name'] + '-team ';
        for team in teamsList:
            if (not (team in self.currentEventInfo['teamChannels'])):
                print('adding new team channel');
                channelObject = self.appClient.channels_create(name=prefix+team);
                print(channelObject['ok']);
                if not channelObject['ok']:
                    print(channelObject);
                self.currentEventInfo['teamChannels'][team] = channelObject['channel']['id'];
        
        self.updateChannels();


    def updateChannels(self,team=None):
        teamsList = [team];
        print('channel updating');
        if (team is None):
            teamsList = self.currentEventInfo['teams'];
        for team in teamsList:
            channelId = self.currentEventInfo['teamChannels'][team];
            obj = channelObj = self.appClient.channels_info(channel=channelId);
            print(obj['ok']);
            if not obj['ok']:
                print(obj) 
            
            if (channelObj['channel']['topic']['value'] is not channels_topic):
                obj = self.appClient.channels_setTopic(channel=channelId,topic=channels_topic);
                print(obj['ok']);
                if not obj['ok']:
                    print(obj) 
            
            correctPurpose = channels_purpose_noscouters.format(team);
            if (team in self.currentEventInfo['teamScouters'] and len(self.currentEventInfo['teamScouters'][team]) > 0):
                correctPurpose = channels_purpose_scouters.format(team) + ', '.join([self.getUsername(user) for user in self.currentEventInfo['teamScouters'][team]]);
            
            if (channelObj['channel']['purpose']['value'] is not correctPurpose):
                obj = self.appClient.channels_setPurpose(channel=channelId,purpose=correctPurpose);
                print(obj['ok']);
                if not obj['ok']:
                    print(obj) 


    def getUsername(self,user):
        userObj = self.appClient.users_info(user=user)['user'];
        if (userObj['profile']['display_name'] != ''):
            return userObj['profile']['display_name'];
        else:
            return userObj['name'];
        
        

    def inEvent(self):
        return not((self.currentEvent is None) or (self.currentEvent == {}));
    def recieve(self,payload):
        data = payload['data']
        print(data);
        web_client = payload['web_client']
        rtm_client = payload['rtm_client']

        scoutingbot_data = web_client.auth_test();
        scoutingbot_id = scoutingbot_data['user_id'];
            
        channel_id = data['channel']
        thread_ts = data['ts']
        user = '';
        isBot = False;
        if ('user' in data):
            user = data['user']
        else:
            isBot = True;
            user = data['bot_id'];
        mentions = self.getMentions(data['text']);
        #self.appClient.chat_postMessage(channel=channel_id,text='HELLO');
        #print(self.getUsername(user));
        if (data['text'].startswith(command_character) and not isBot):
            command_args = data['text'][1:].split(' ');
            num_args = len(command_args);
            if (command_args[0] == 'event'):
                if (num_args == 1):
                    web_client.chat_postMessage(channel=channel_id,text=f'Error in command syntax. Please use {command_character}event help to see a list of the event commands.');

                if (num_args >= 2 and command_args[1] == 'help'):
                    texts = [f'Help for scouters commands:', f'{command_character}event help - get help for the event commands', f'{command_character}event start [name] - start a new event with the name [name]. There must not be an event in session, and the name must not have been used in any previous events.', f'{command_character}event end - ends the current event and archives the team channels',f'{command_character}event open [name] - opens a previous event [name] and unarchives the team channels. The event functions as normal from that point. [name] must be in the list of previous events per below.',f'{command_character}event previous - displays the list of all previous events. See above.', f'{command_character}event teams - list the teams registered in the current event', f'{command_character}event teams set [team1] [team2] [team3] - set the current teams at the event (and create team channels if there aren\'t already'];
                    web_client.chat_postMessage(channel=channel_id,text='\n'.join(texts));
                    
                if (num_args >= 2 and command_args[1] == 'start'):
                    return_msg = '';
                    if num_args == 2:
                        return_msg = f'Error in command syntax: please follow format {command_character}event start [event_name]';
                    elif num_args == 3:
                        return_msg = self.startEvent(command_args[2]);
                    else:
                        return_msg = f'Error in command syntax: please do not uses spaces in names - use underscores instead.';
                    if (return_msg is not None and return_msg != ''):
                            web_client.chat_postMessage(channel=channel_id,text=return_msg);
                if (num_args >= 2 and command_args[1] == 'end'):
                    return_msg = self.endEvent();
                    if (return_msg is not None and return_msg != ''):
                        web_client.chat_postMessage(channel=channel_id,text=return_msg);

                if (num_args >= 2 and command_args[1] == 'previous'):
                    return_msg = self.getPreviousEvents();
                    if (return_msg is not None and return_msg != ''):
                        web_client.chat_postMessage(channel=channel_id,text=return_msg);

                if (num_args >= 2 and command_args[1] == 'info'):
                    return_msg = self.eventInfo();
                    if (return_msg is not None and return_msg != ''):
                        web_client.chat_postMessage(channel=channel_id,text=return_msg);
                
                if (num_args >= 2 and command_args[1] == 'open'):
                    return_msg = None;
                    if (num_args < 3):
                        return_msg = f'Error in command syntax: please specify name of previous event to open';
                    elif (num_args >3):
                        return_msg = f'Error in command syntax: please do not use spaces in names. If an event happenned, it had no spaces. \nTry underscores, or use {command_character}event previous to get a list of the previous events';
                    else:
                        return_msg = self.openEvent(command_args[2]);
                    if (return_msg is not None and return_msg != ''):
                        web_client.chat_postMessage(channel=channel_id,text=return_msg);

                if (num_args >= 2 and command_args[1] == 'teams'):
                    return_msg = '';
                    if (num_args == 2):
                        return_msg = self.teamsList();
                    
                    elif (num_args > 3 and command_args[2] == 'set'):
                        teams = command_args[3:];
                        return_msg = self.setTeams(teams);
                    
                    if (return_msg is not None and return_msg != ''):
                        web_client.chat_postMessage(channel=channel_id,text=return_msg);

            if (command_args[0] == 'scouters'):
                if (num_args == 1):
                    web_client.chat_postMessage(channel=channel_id,text=f'Error in command syntax. Please use {command_character}scouters help to see a list of the scouters commands.');

                if (num_args >= 2 and command_args[1] == 'help'):
                    texts = [f'Help for scouters commands:', f'{command_character}scouters help - get help for the scouters command', f'{command_character}scouters get [team number | @scouter] - get info on who\'s scouting what team. Also returns links to the team channels', f'{command_character}scouters list - list users scouting teams in the current event', f'{command_character}scouters add [@user1] [@user2] [...] [team number 1] [team number 2] [...] - add scouters scouting teams. Will add the specified teams to each of the users\'s teams lists.', f'{command_character}scouters remove [@user1] [@user2] [...] [team1] [team2] [...] - removes each team from the specified users\' teams lists (if they exist).'];
                    [web_client.chat_postMessage(channel=channel_id,text=text) for text in texts]        

                if (num_args >= 2 and command_args[1] == 'get'):
                    return_msg = None;
                    if (num_args == 2):
                        return_msg = f'Error in command syntax: please specify either a team number or a mention a scouter with syntax {command_character}scouters get [team number | @scouter] \n(remember to mute pings in #scouting if you haven\'t already so you can use mentions';
                    elif self.isMention(command_args[2]):
                        user = self.getMentions(command_args[2])[0];
                        return_msg = self.getScouterTeams(user,self.getUsername(user));
                    else:
                        return_msg = self.getTeamScouters(command_args[2]);
                    if (return_msg is not None and return_msg != ''):
                        web_client.chat_postMessage(channel=channel_id,text=return_msg);

                if (num_args >= 2 and command_args[1] == 'list'):
                    return_msg = self.listScouters();
                    if (return_msg is not None and return_msg != ''):
                        web_client.chat_postMessage(channel=channel_id,text=return_msg);

                if (num_args >= 2 and command_args[1] == 'add'):
                    return_msg = None;
                    if (num_args < 4):
                        return_msg = f'Error in command syntax: please specify both the names and teams to add scouters with the syntax {command_character}scouters add @[name1] @[name2] @[name...] [team number 1] [team number 2] [team number ...]';
                    elif (len(mentions) == 0):
                        return_msg = f'Error in command syntax: please specify both the names and teams to add scouters with the syntax {command_character}scouters add @[name1] @[name2] @[name...] [team number 1] [team number 2] [team number ...]';
                    else:
                        non_mention_args = [arg for arg in command_args[2:] if (not(self.isMention(arg)))];
                        return_msg = self.addScouter(mentions,non_mention_args);
                    if (return_msg is not None and return_msg != ''):
                        web_client.chat_postMessage(channel=channel_id,text=return_msg);

                if (num_args >= 2 and command_args[1] == 'remove'):
                    return_msg = None;
                    if (num_args < 4):
                        return_msg = f'Error in command syntax: please specify both the names and teams to remove scouted teams with the syntax {command_character}scouters remove @[name1] @[name2] @[name...] [team number 1] [team number 2] [team number ...]';
                    elif (len(mentions) == 0):
                        return_msg = f'Error in command syntax: please specify both the names and teams to remove scouted teams with the syntax {command_character}scouters remove @[name1] @[name2] @[name...] [team number 1] [team number 2] [team number ...]';
                    else:
                        non_mention_args = [arg for arg in command_args[2:] if (not(self.isMention(arg)))];
                        return_msg = self.removeScouter(mentions,non_mention_args);
                    if (return_msg is not None and return_msg != ''):
                        web_client.chat_postMessage(channel=channel_id,text=return_msg);






                


##    
##    if len(mentions) > 0:
##        if (scoutingbot_id in mentions):
##            web_client.chat_postMessage(
##                channel=channel_id,
##                text=f"<@{user}> pinged me rEEEEEE");
##    elif 'Hello' in data['text']:
##        web_client.chat_postMessage(
##            channel=channel_id,
##            text=f"Hi <@{user}>!",
##            thread_ts=thread_ts
##        )

botthing = None;

@slack.RTMClient.run_on(event='message')
def recieve_message(**payload):
        botthing.recieve(payload);

if __name__ == '__main__':
    botthing = bot();
    rtm_client = slack.RTMClient(token=slack_token)
    rtm_client.start()


