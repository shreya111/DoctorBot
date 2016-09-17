import os
import sys
import json

import requests
import apiai
from diagnose import diagnose, apiai_symptom
import sqlite3
import urllib, json
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

    return "Hello!", 200


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

                    # sort different types of messages
                    message = messaging_event["message"]
                    if message.get("text"): # get message
                        message = message["text"]
                        if message == "DoctorBot":
                            init_buttom_template(sender_id)
                        else:
                            send_message(sender_id, "For medical advice, enter 'DoctorBot'.")





                    # if message.get("text"): # get message
                    #     message = message["text"]
                    #     if symptom_mode:
                    #         symptoms = 3
                    #         print symptoms
                    #         # if symptom == None
                    #         #     symptom = apiai_symptom(message) # assuming user put symptom
                    #         # elif 


                    #     elif alert_mode:
                    #         pass
                    #     else:
                    #         if message == "Hi":
                    #             init_buttom_template(sender_id)
                    #         else:
                    #             send_message(sender_id, "Say 'Hi' to the DoctorBot to get started!")

                    # elif message.get("attachments"):    # get attachment
                    #     attach = message["attachments"][0]  # loop over attachments?
                    #     if attach["type"] == "location":
                    #         latitude = attach["payload"]["coordinates"]["lat"]
                    #         longitude = attach["payload"]["coordinates"]["long"]
                    #         clinic_type = "hospital"
                    #         clinicsURL = "https://api.foursquare.com/v2/venues/search?ll="+str(latitude)+","+str(longitude)+"&radius=15000&query="+clinic_type+"&client_id=1TCDH3ZYXC3NYNCRVL1RL4WEGDP4CHZSLPMKGCBIHAYYVJWA&client_secret=VASKTPATQLSPXIFJZQ0EZ4GDH2QAZU1QGEEZ4YDCKYA11V2J&v=20160917"
                    #         r = urllib.urlopen(clinicsURL)
                    #         data = json.loads(r.read())
                    #         hospitals = []
                    #         latitudes = []
                    #         longitudes = []
                    #         venues = data["response"]["venues"]
                    #         if len(venues) > 3:
                    #             maxi = 3
                    #         else:
                    #             maxi = len(venues)
                    #         for x in range(0, maxi):
                    #             hospitals.append(venues[x]["name"])
                    #             send_message(sender_id, "Option #"+str(x+1)+": "+venues[x]["name"])
                    #             latitudes.append(venues[x]["location"]["lat"])
                    #             longitudes.append(venues[x]["location"]["lng"])
                    #         message = "Location: " + str(latitude) + ", " + str(longitude)

                    #         mapurl = "https://maps.googleapis.com/maps/api/staticmap?center="+str(latitude)+","+str(longitude)+"&markers=color:green%7C"+str(latitude)+","+str(longitude)+"&key=AIzaSyB1CFi3ImDxL21QTu7EN2e-RvP2LPAJgiY&size=800x800"
                    #         for y in range(0,maxi):
                    #             mapurl = mapurl +"&markers=color:red%7Clabel:H%7C"+str(latitudes[y])+","+str(longitudes[y])
                    #         send_message(sender_id, "And here they are on a map :)")
                    #         #sendImage
                    #         send_message(sender_id, mapurl)
                    #     elif attach["type"] == "image":
                    #         image_url = attach["payload"]["url"]
                    #         message = "Image url: " + image_url
                    #         send_message(sender_id, message)

                    # if message is not None and message != "Hi":
                    #     log(message)
                    #     send_message(sender_id, message) "Say 'Hi' to the DoctorBot to get started!")

                # if messaging_event.get("delivery"):  # delivery confirmation
                #     pass

                # if messaging_event.get("optin"):  # optin confirmation
                #     pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]
                    message = messaging_event["postback"]["payload"]
                    send_message(sender_id, message)
                    # if message == 'In order to properly help you, I will \
                    #     need to ask you a few questions. What symptoms do you have?':
                    #     symptom_mode = True
                    # elif message == 'Which diseases and/or symptoms would you like to check in your local area?':
                    #     alert_mode = True
    return "ok", 200

def send_message(sender_id, message_text):

    log("sending message to {recipient}: {text}".format(recipient=sender_id, text=message_text))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": sender_id
        },
        "message": {
            "text": message_text
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


def init_buttom_template(sender_id):

    # get user info
    r = requests.get('https://graph.facebook.com/v2.6/'+recipient_id+
        '?fields=first_name,last_name,profile_pic,locale,timezone,gender&access_token='
        +os.environ["PAGE_ACCESS_TOKEN"])
    try:
        first_name = str(r.json()["first_name"])
    except:
        first_name = ""
    try:
        last_name = str(r.json()["last_name"])
    except:
        last_name = ""
    try:
        gender = str(r.json()["gender"])
    except:
        gender = ""
    try:
        profile_pic = str(r.json()["profile_pic"])
    except:
        profile_pic = ""

    welcome_message = "Hello! How may I help you?"
    if gender is not "":
        if gender == 'male':
            welcome_message = "Hello Mr."+" "+first_name+" "+last_name + "! How may I help you?"
        else:
            welcome_message = "Hello Ms."+" "+first_name+" "+last_name + "! How may I help you?"
    else:
        welcome_message = "Hello "+first_name+" "+last_name + "! How may I help you?" 

    log("Sending button template to {recipient}.".format(recipient=sender_id))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": sender_id
        },
        "message":{
            "attachment":{
                "type":"template",
                "payload":{
                    "template_type":"button",
                    "text": welcome_message,
                    "buttons":[
                        {
                        'type': 'postback',
                        'title': 'Symptom checker',
                        'payload': 'In order to properly help you, I will need to ask you a few questions. What symptoms do you have?'
                        },
                        {
                        'type': 'postback',
                        'title': 'Health alerts',
                        'payload': 'Which diseases and/or symptoms would you like to check in your local area?'
                        }
                    ]
                }
            }
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)

    log(r.text)


def log(message):  # simple wrapper for logging to stdout on heroku
    print str(message)
    sys.stdout.flush()


if __name__ == '__main__':
    app.run(debug=True)
