from urllib import request, parse
import json
from common.logger import Logger

def create_slack_embed(title="", text=""):
    return {
        "text": "{}".format(text)
    }

def send_message_to_slack(content, url, logger=None):
    '''send a message to slack (expects a dict)'''

    log_err = lambda x: logger.error(x) if logger != None else None
    log_war = lambda x: logger.warning(x) if logger != None else None
    log_inf = lambda x: logger.info(x) if logger != None else None

    post = content

    try:
        json_data = json.dumps(post)
        req = request.Request(url, data=json_data.encode('ascii'), headers={'Content-Type': 'application/json'})
        resp = request.urlopen(req)
        log_inf("Message sent to Slack")
    except Exception as err:
        log_err("Error sending message to Slack: {}".format(content))