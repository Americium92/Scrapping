import pandas as pd
import requests
from requests_html import HTML
from requests_html import HTMLSession
import inspect
from bs4 import BeautifulSoup
from datetime import datetime
import time
import json
import logging
import dotenv
import traceback
import re

CONFIG = dotenv.dotenv_values()


#define our URL
url = 'https://tickets.formula1.com/fr'
GP = []
img = "http://toussticks.fr/832-thickbox_default/formula-1-f1-nouveau-logo-monochrome.jpg"
Webhook = "https://discord.com/api/webhooks/1023348115685769368/m8BH1Z4swlAAzpeBOWUP7kYZuyVyVHQa7hbl9gXX9iy3dhyP3mVe9AuA2DWZaCx6_y8R"

def discord_webhook(title, description, thumbnail, url):
    """
    Sends a Discord webhook notification to the specified webhook URL
    """
    data = {
        "username": CONFIG['USERNAME'],
        "avatar_url": CONFIG['AVATAR_URL'],
        "embeds": [{
            "title": title,
            "description": description,
            "thumbnail": {"url": thumbnail},
            "url": url,
            "color": int(CONFIG['COLOUR']),
            "footer": {'text': 'Made by Sledeme'},
            "timestamp": str(datetime.utcnow())
        }]
    }

    result = requests.post(Webhook, data=json.dumps(data), headers={"Content-Type": "application/json"})

    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
        logging.error(msg=err)
    else:
        print("Payload delivered successfully, code {}.".format(result.status_code))
        logging.info(msg="Payload delivered successfully, code {}.".format(result.status_code))



#use the session to get the data
session = HTMLSession()
response = session.get(url)

#Render the page, up the number on scrolldown to page down multiple times on a page
response.html.render()

#take the rendered html and find the element that we are interested in
dates = response.html.find('div.grid-template-2 p.event-date')
dispo = response.html.find('div.grid-template-2 a.event-link')

for i in range(len(dates)) :
    ticket_achat = []
    lien = str(dispo[i].attrs['href'])
    resum = dates[i].text + dispo[i].text

    if dispo[i].text == "COMMANDER" :
        dispo[i] = "en vente"
    else :
        dispo[i] = "mise en vente prochainement"

    # place restante
    session = HTMLSession()
    place = session.get("https://tickets.formula1.com" + lien)
    place.html.render()

    restant = place.html.find('div.grandstand-options-item')
    for ticket in restant :
        ticket_achat.append(ticket.text + "\n")
    print(ticket_achat)

    if resum in GP :
        print("")
    else :
        GP.append(resum)
        time.sleep(1)
        discord_webhook(dates[i].text,dispo[i] + "\n" + ' '.join(ticket_achat) , img, "https://tickets.formula1.com" + lien)


