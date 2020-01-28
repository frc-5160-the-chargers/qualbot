import slack
import logging
import json
import datetime

tokens_file = "slack_tokens.json";
with open(tokens_file) as f:
    tokens = json.load(f);
    slack_token = tokens["bot_token"];
    app_token = tokens["app_token"];





    
class bot:
    


    # message json example: {"channel":"C061EG9SL","text":"I hope the tour went well, Mr. Wonka.","attachments":[{"text":"Who wins the lifetime supply of chocolate?","fallback":"You could be telling the computer exactly what it can do with a lifetime supply of chocolate.","color":"#3AA3E3","attachment_type":"default","callback_id":"select_simple_1234","actions":[{"name":"winners_list","text":"Who should win?","type":"select","data_source":"users"}]}]}

    
    def __init__(self):
        self.appClient = slack.WebClient(token=app_token);
        print(self.appClient.rtm_connect());
        #print(self.appClient.auth_test());

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
        elif('bot_id' in data):
            isBot = True;
            user = data['bot_id'];
        else:
            return;
        self.appClient.chat_postMessage(channel=channel_id,text='HELLO');


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
    ssl_context = ssl_lib.create_default_context(cafile=certifi.where());
    rtm_client = slack.RTMClient(timeout=60,token=app_token);
    rtm_client.start();


