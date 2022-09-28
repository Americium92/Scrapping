import pandas as pd
from requests_html import HTML
from requests_html import HTMLSession
import inspect
from bs4 import BeautifulSoup
from datetime import datetime
import time

#define our URL
url = 'https://tickets.formula1.com/fr'
GP = []
img = "http://toussticks.fr/832-thickbox_default/formula-1-f1-nouveau-logo-monochrome.jpg"

#use the session to get the data
session = HTMLSession()
response = session.get(url)

#Render the page, up the number on scrolldown to page down multiple times on a page
response.html.render()

#take the rendered html and find the element that we are interested in
dates = response.html.find('div.grid-template-2 p.event-date')
dispo = response.html.find('div.grid-template-2 a.event-link')

for i in range(len(dates)) :
    print("\n")
    print(dates[i].text + "\n" + dispo[i].text)
    print(dispo[i].links)
    resum = dates[i].text + dispo[i].text
    if resum in GP :
                print("")
    else :
        GP.append(resum)
        time.sleep(1)
        #discord_webhook(resum, info, images_V, "https://tickets.formula1.com" + dispo[i].links)