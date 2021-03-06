from flask import Flask, render_template, jsonify
import getpass
import sys
import telnetlib
import requests
import socket
#socket.getaddrinfo('127.0.0.1', 5000)
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from wit import Wit
import os
from apixu.client import ApixuClient

#api_key = os.environ['6ccd8584cdc2431f82a35428191703']
clientWeather = ApixuClient('6ccd8584cdc2431f82a35428191703')

WIT_TOKEN = "I5Z52AJQR7MCBVZDW5SPVUPERS4SJ5P5"

PORT_NUMBER = 8080
SPOTIPY_CLIENT_ID = "79d4b9443c804d1c84ecb8190dcf4898"
SPOTIPY_CLIENT_SECRET = "c9e17ddc434b4aa09a48b8d02a83f1c1"
SPOTIPY_REDIRECT_URI = 'http://localhost:8080'
SCOPE = 'user-library-read'
CACHE = '.spotipyoauthcache'

client_credentials_manager = SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)
spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

app = Flask(__name__)

client = Wit(WIT_TOKEN)


def validationMessage(income):

    resp = client.message(income)
    print('Response: {}'.format(resp))

    HOST = "192.168.1.5"

    dict={
        "Prender luces": "Luces encendidas",
        "prender luces": "Luces encendidas",
        "Apagar luces": "Luces apagadas",
        "apagar luces": "Luces apagadas",
        "state?": "state",
        "State?": "state",
        "Estado?": "state",
        "estado?": "state",
        "estado": "state",
        "state": "state",
        "Turn On" : "Luces encendidas",
        "Turn Off" : "Luces apagadas",
        "turn on" : "Luces encendidas",
        "turn off" : "Luces apagadas"
    }

    outgoing_message = ""

    if 'luz' in resp['entities']:
        incoming_message=resp['entities']['luz'][0]['value']
        if(incoming_message == "on"):
                req = requests.get("http://"+HOST+"/on")
                outgoing_message="Luces Prendidas"
		print(req.text)
        elif(incoming_message == "off"):
		outgoing_message="Luces Apagadas"
                req = requests.get("http://"+HOST+"/off")
        else:
            req = requests.get("http://"+HOST+"/state")
            state = ""
            if(req.text == "Off"):
                state = "OFF"
            else:  
                state = "ON"
            outgoing_message = "The current light state is: " + state
    elif 'spotify' in resp['entities']:
        incoming_message=resp['entities']['spotify'][0]['value']
        if(incoming_message == "info"):
            banda = resp['_text'].replace("spotify", "")
            banda = banda.replace("info", "")
            outgoing_message = search_song(banda)
        if(incoming_message == "open"):
            banda = resp['_text'].replace("spotify", "")
            banda = banda.replace("open", "")
            outgoing_message = get_linkTo(banda)
    elif 'intent' in resp['entities']:
        if 'clima' == resp['entities']['intent'][0]['value']:
            for item in resp['entities']['location'][0]['resolved']['values']:
                if("wikipedia" in item['external']):                         
                    current = clientWeather.current(q=item['external']['wikipedia'])
                    text = current['location']['name'] + "\n"
                    text += current['location']['region'] + "\n"
                    text += "Current temperature is: \n"
                    text += str(current['current']['temp_c']) +"\n"
                    text += "-------------- \n"
                    outgoing_message += text
        if 'puerta' == resp['entities']['intent'][0]['value']:
            incoming_message=resp['entities']['intent'][0]['value']
            print("Connecting to ->")
            req = requests.get("http://192.168.43.183:5000/quien_es")
            outgoing_message = "People will be in this URL -> http://192.168.43.183:5000/static/detection/FotoPuerta.jpg \n"
            outgoing_message += req.content
    else:
        outgoing_message = "Sorry! I don't recognize that instruction. Please try again"

    return outgoing_message

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/<id_root>/<instruction>")
def send_instruction(id_root, instruction):

    print(instruction)
    message = validationMessage(instruction)

    return message
    #return jsonify("SERVER ->"+ id_root + "\nACTIONS -> "+ instruction)

@app.route("/search/<name>")
def search_song(name):
    print("info",name)
    name = name.replace("info", "")
    results = spotify.search(q='artist:' + name, type='artist')
    items = results['artists']['items']
    if len(items) > 0:
        artist = items[0]
        text_complete = "The band name is "+artist['name']+"\n"
        text_complete += "His popularity is "+str(artist['popularity'])+"% \n"
        text_complete += "Play genres like: "+" ".join(artist['genres'])+"\n"
        text_complete += "Has a lot of followers, precisly "+str(artist['followers']['total'])+"\n"
    else:
        text_complete = "Write better the name, using ""info *the band whatever you want*"""
    return text_complete
    #return items

def get_linkTo(name):
    print("open",name)
    name = name.replace("abrir", "")
    results = spotify.search(q='artist:' + name, type='artist')
    items = results['artists']['items']
    if len(items) > 0:
        artist = items[0]
        text = artist['external_urls']['spotify']
    else:
        text = "No artist find"    
    return text
