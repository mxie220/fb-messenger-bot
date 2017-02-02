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
        word = word.lower().strip('?').strip('.').strip('!')
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
    if "hi" in text or "hey" in text or "hello" in text or "greetings" in text:
        return greetings_list[n]
    elif "good" in text and "morning" in text:
        return "Good Morning!\n"
    elif "good" in text and "evening" in text:
        return "Good Evening!\n"
    elif "good" in text and "afternoon" in text:
        return "Good Afternoon!\n"
    elif "goodbye" in text or "bye" in text:
        return "Goodbye!"
    else:
        return ""

def info(text):
    aboutscope = "Scope is a fun way to help you\
    connect with those around you immediately in real life.\n"
    if "what" in text and "is" in text and "scope" in text:
        return aboutscope
    elif "tell" in text and "me" in text and "about" in text:
        return aboutscope
    elif "about" in text and "scope" in text:
        return aboutscope
    elif "interview" in text or "another" in text and "question" in text and "next" in text or "market" in text and "research" in text or "interviews" in text:
        return interview()
    elif "who" in text or "what" in text and "you" in text and "are" in text:
        return "My name is Scopey.\nAsk me anything about Scope!\n"
    elif "how" in text and "use" in text or "setup" in text or "1" in text or "instructions" in text or "instruction" in text or "info" in text or "set" in text and "up" in text:
        return instructions(1)
    elif "2" in text:
        return instructions(2)
    elif "3" in text:
        return instructions(3)
    elif "4" in text:
        return instructions(4)
    elif "5" in text:
        return instructions(5)
    elif "6" in text:
        return instructions(6)
    elif "help" in text:
        return "How may I help you?\n"
    else:
        return ""

def date(text):
    if "date" in text or "today" in text:
        date = datetime.datetime.today()
        return date.strftime("Today is %A the %d of %B. \n")
    elif "time" in text:
        time = datetime.datetime.now()
        return time.strftime("It is currently %I:%M%p. \n")
    else:
        return ""

def instructions(step):
    if step == 1:
        return "Download and install the Scope app on your iOS or Android phone.\
        \n\nMessage me the number '2' once you have completed."
    elif step == 2:
        return "Open up the app and choose one of the following options:\n1. Go on a date\n2. Meet a new friend\n3. Network with people\n\nMessage me the number '3' once you have completed."
    elif step == 3:
        return "Now choose one of the following options to connect into Scope.\n\nMessage me the number '4' once you have completed."
    elif step == 4:
        return "Take a selfie - make sure it's a good angle.\n\nMessage me the number '5' once you have completed."
    elif step == 5:
        return "Set up your profile by choosing:\n1. Who you're interested in\n2. The ages you're interested in\n3. How far you're willing to walk\n4. Optional: use this only if you're looking for someone very specific\nThen press 'Save'\n\nMessage me the number '6' once you have completed."
    elif step == 6:
        return "Congratulations! You're now ready to Scope.\n"
    else:
        return "Message me the number '1' to set up."


def interview():
    num = random.randrange(1, 10)
    if num == 1:
        return "Do you find it easier to have a conversation with someone online \
or offline?"
    elif num == 2:
        return "Would you be more likely to talk to someone if you knew they \
wouldn't mind being approached?"
    elif num == 3:
        return "What do you think about online dating or dating apps?"
    elif num == 4:
        return "Do you think there is a difference between online dating and \
dating apps?"
    elif num == 5:
        return "If there is anything you can change about dating apps or online \
dating, what would it be?"
    elif num == 6:
        return "Do you have an iPhone or an Android?"
    elif num == 7:
        return "How much are you willing to pay for a dating app if you knew it \
was reliable and had a good reputation?"
    elif num == 8:
        return "Are there many couples that you know of who met online?"
    elif num == 9:
        return "Would you ever connect your personal life with your professional \
life or do you prefer to keep them separate?"
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
