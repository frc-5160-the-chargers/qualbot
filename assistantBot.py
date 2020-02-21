from flask import Flask, request, json
import json, threading, requests

app = Flask(__name__)

with open(r"teamCreation\slack_tokens.json") as tokenFile:
    fileContents = json.load(tokenFile)
token = fileContents["web_token"]

@app.route("/slack", methods=["POST"])
def serve_slack():
    slack_request = request.form

    x = threading.Thread(
        target=processing, args=(slack_request,)
    )
    x.start()
    return ""

def processing(slack_request):
    response_url = slack_request["response_url"]
    message = {"response_type": "in_channel", "text": "I work"}
    res = requests.post(response_url, json=message)

if __name__ == "__main__":
    app.run()