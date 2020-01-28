import json
import slack

@slack.RTMClient.run_on(event="message")
def reply_message(**payload):
    with open('config.json', 'r') as f:
        prefix = json.load(f)['prefix']

    data = payload['data']
    web_client = payload['web_client']
    if 'subtype' not in data: # we know it's (probably) a plain message
        text = data['text'].lower()
        if text.startswith(prefix):
            do_stuff()

if __name__ == '__main__':
    with open('slack_tokens.json', 'r') as f:
        secrets = json.load(f)
        slack_token = secrets["app_token"]
    
    rtmclient = slack.RTMClient(token=slack_token)
    rtmclient.start()
