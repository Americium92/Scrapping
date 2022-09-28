import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time

import json
import logging
import dotenv
import traceback

CONFIG = dotenv.dotenv_values()
MATCH = []

url = 'https://billetterie.psg.fr/fr/'

####################
## Envoie Discord ##
####################

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

    result = requests.post(CONFIG['WEBHOOK'], data=json.dumps(data), headers={"Content-Type": "application/json"})

    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
        logging.error(msg=err)
    else:
        print("Payload delivered successfully, code {}.".format(result.status_code))
        logging.info(msg="Payload delivered successfully, code {}.".format(result.status_code))

###########
## DISPO ##
###########

def dispo_place(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    divs = soup.find_all("div", class_="p:20px p:40px@768px psgMatchOffersLytList")
    for div in divs: 
        types = div.find_all("div",class_="flex psgMatchPrdHeader flexcolumn@0-839px stack:10px@0-839px")
        for type in types:
            images_V = type.findAll('h2')


##########
## MAIN ##
##########

while True:
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    divs = soup.find_all("div", class_="relative psgCptMatchCard overflow:hidden mx:-20px@0-1239px p:30px-20px p:30px@1240px radius:4px@1240px bgp:100%-100% bgr:no-repeat")
    
    for div in divs:
        ## Recup info
        domicile = div.find("span","psgTeamName psgTeamName--receiving")
        adversaire = div.find("span","psgTeamName psgTeamName--visiting")
        championnat = div.find("span","fs:9px psgMatchCat lh:1.2 tt:uppercase")
        info = div.find("time",class_="psgMatchDate fs:18px lh:1 tt:uppercase").text

        ## Recup logo
        logo_V = div.find("span",class_="psgTeamLogo psgTeamLogo--receiving")
        images_V = logo_V.findAll('img')[0]['src']
        logo_V = div.find("span",class_="psgTeamLogo psgTeamLogo--visiting")
        images_V = logo_V.findAll('img')[0]['src']
        print(images_V)
    
        ## Resumé du match
        resum = str(championnat.text + domicile.text + "-" + adversaire.text)

        ## Boucle d'envoie
        pre_link = div.find_all("div", class_="flex psgMatchCardLinks jc:space-between psgMatchCardLinks--fixed")
        for links in pre_link:
            link = links.find("a")
            if resum in MATCH :
                print("")
            else :
                MATCH.append(resum)
                time.sleep(1)
                dispo_place("https://billetterie.psg.fr" + link['href'])
                discord_webhook(resum, info, images_V, "https://billetterie.psg.fr" + link['href'])




    

