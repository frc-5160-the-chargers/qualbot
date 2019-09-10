import os
import time
import re
import slack
import logging

slack_token = 'xoxb-26662449251-753606403860-XKnFx1qoSEjax7ZAdzAkPmDJ'

scoutingbot_data = None;
scoutingbot_id = '';


RTM_READ_DELAY = 1;
EXAMPLE_COMMAND = "do";
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"


def getMentions(text):
    mentionObjects = re.findall(MENTION_REGEX,text);
    mentions = [obj[0] for obj in mentionObjects];
    return mentions;

@slack.RTMClient.run_on(event='message')
def recieve_message(**payload):
    data = payload['data']
    print(data);
    web_client = payload['web_client']
    rtm_client = payload['rtm_client']

    scoutingbot_data = web_client.auth_test();
    scoutingbot_id = scoutingbot_data['user_id'];
        
    channel_id = data['channel']
    thread_ts = data['ts']
    user = '';
    if ('user' in data):
        user = data['user']
    else:
        user = data['bot_id'];
    mentions = getMentions(data['text']);
    if len(mentions) > 0:
        if (scoutingbot_id in mentions):
            web_client.chat_postMessage(
                channel=channel_id,
                text=f"<@{user}> pinged me rEEEEEE");
    elif 'Hello' in data['text']:
        web_client.chat_postMessage(
            channel=channel_id,
            text=f"Hi <@{user}>!",
            thread_ts=thread_ts
        )


rtm_client = slack.RTMClient(token=slack_token)
rtm_client.start()


