import os
import sys
import json

import datetime
import random

import requests
from flask import Flask, request

app = Flask(__name__)


@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello this is Scopey from Scope!", 200


@app.route('/', methods=['POST'])
def webhook():

    # endpoint for processing incoming messaging events

    data = request.get_json()
    log(data)  # you may not want to log every incoming message in production, but it's good for testing

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):  # someone sent us a message

                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    message_text = messaging_event["message"]["text"]  # the message's text
                    
                    message = message_to_send(message_text)

                    send_message(sender_id, message)

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass

    return "ok", 200


def message_to_send(message_text):
    message_list = message_text.split(' ')
    md = {}
    for word in message_list:
        word = word.lower().strip('?').strip('.').strip('!').strip('"')
        if word in md:
            md[word] += 1
        else:
            md[word] = 0

    message_back = response(md)
    return message_back

def response(m):
    g = greetings(m)
    i = info(m)
    d = date(m)
    return g + i + d


def greetings(text):
    greetings_list = ["Hi ", "Hello ", "Hey "]
    n = random.randrange(0, 3)
    if "good" in text and "morning" in text:
        return "Good Morning!\n"
    elif "good" in text and "evening" in text:
        return "Good Evening!\n"
    elif "good" in text and "afternoon" in text:
        return "Good Afternoon!\n"
    else:
        return greetings_list[n]

def info(text):
    aboutscope = "Scope is a social, networking, and dating app that helps you \
    connect with those around you in real life, in real time.\n"
    instructionsope = "instructions"
    if "what" in text and "is" in text and "scope" in text:
        return aboutscope
    elif "tell" in text and "me" in text and "about" in text:
        return aboutscope
    elif "how" in text and "use" in text:
        return instructionsope
    elif "help" in text:
        return "How may I help you?\n"
    else:
        return ""

def date(text):
    if "date" in text or "today" in text:
        date = datetime.date.today()
        return date.strftime("Today is %A the %d of %B. \n")
    else:
        return ""



def send_message(recipient_id, message_text):

    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


def log(message):  # simple wrapper for logging to stdout on heroku
    print str(message)
    sys.stdout.flush()


if __name__ == '__main__':
    app.run(debug=True)
