import requests
from bs4 import BeautifulSoup
import json
import os
import dotenv
from datetime import datetime
import logging
import threading
import time

CONFIG = dotenv.dotenv_values()

def discord_webhook(Webhook, title, description, thumbnail, url):
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

def TCGspeed() :
    Webhook = "https://discord.com/api/webhooks/1366092712197226536/HFfCTSK1u5DkqxHB8KXThNORfTOamwqgfjDgJAx4MZtyd1V9b3E7TIQwsyiuU83Gw32E"
    # URL de la page à scraper
    url = 'https://tcgspeed.com/collections/ev08-5-evolutions-prismatiques'

    # Chemin du fichier JSON
    json_file_path = 'produits.json'

    while True :
        # Charger les données existantes du fichier JSON
        if os.path.exists(json_file_path):
            with open(json_file_path, 'r') as file:
                produits = json.load(file)
        else:
            produits = []

        # Envoyer une requête GET à la page
        response = requests.get(url)

        # Vérifier si la requête est réussie
        if response.status_code == 200:
            # Analyser le contenu de la page avec BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Trouver tous les conteneurs de produits
            product_containers = soup.find_all('div', class_='product-card')
            
            # Boucle pour extraire les informations de chaque produit
            for product in product_containers:
                # Extraire le titre du produit
                title = product.find('div', class_='h4 grid-view-item__title product-card__title').text.strip()
                
                # Extraire le prix du produit
                price = product.find('span', class_='price-item price-item--regular').text.strip()

                # Trouver la balise img avec la classe 'list-view-item__image'
                image_tag = product.find('img', class_='list-view-item__image')
                if image_tag:
                    img_url = image_tag.get('src')
                    full_img_url = 'https:' + img_url  # Compléter l'URL relative de l'image
                else:
                    full_img_url = None

                # Extraire le lien d'achat du produit
                link = product.find('a', class_='grid-view-item__link grid-view-item__image-container full-width-link')['href']
                full_link = f'https://tcgspeed.com{link}'

                # Extraction disponibilité
                # Envoyer une requête GET aux pages filles
                fille = requests.get(full_link)
                if fille.status_code == 200:
                    # Analyser le contenu de la page avec BeautifulSoup
                    soup_dispo = BeautifulSoup(fille.content, 'html.parser')
                    dispo = soup_dispo.find('button', class_='btn product-form__cart-submit').text.strip()
                else:
                    dispo = None

                # Créer un dictionnaire pour le produit
                produit = {
                    'title': title,
                    'price': price,
                    'image_url': full_img_url,
                    'link': full_link,
                    'dispo': dispo
                }

                # Vérifier si le produit est déjà dans le JSON
                found = False
                for existing_product in produits:
                    if existing_product['title'] == title and existing_product['price'] == price:
                        found = True
                        # Mettre à jour la disponibilité si elle a changé
                        if existing_product['dispo'] != dispo:
                            discord_webhook(
                                Webhook=Webhook,
                                title=f"tcgspeed : \n{title}",
                                description=f"{title}. \nNouvelle disponibilité: {dispo}",
                                thumbnail=full_img_url,
                                url=full_link
                            )
                            existing_product['dispo'] = dispo
                        break

                # Si le produit n'est pas trouvé, l'ajouter au JSON et envoyer une notification
                if not found:
                    produits.append(produit)
                    discord_webhook(
                        Webhook=Webhook,
                        title=f"tcgspeed : \n{title}",
                        description=f"{title}.\nPrix: {price}\nDisponibilité: {dispo}",
                        thumbnail=full_img_url,
                        url=full_link
                    )

            # Enregistrer les données mises à jour dans le fichier JSON
            with open(json_file_path, 'w') as file:
                json.dump(produits, file, indent=4, ensure_ascii=False)

            print('Les informations des produits ont été mises à jour avec succès.')
        else:
            print('Erreur lors de la récupération de la page.')
        time.sleep(1)

def Hikaru():
    # URL de la page à scraper
    Webhook = "https://discord.com/api/webhooks/1366092861753524436/6WDgQM2MNGNhm5F-6FsCfxQ2FAwvdxoMGDFsbVCOixoNAd65vaDKdJY2TpkOhoHgmB6b"
    url = 'https://hikarudistribution.com/collections/pokemon-francais?sort_by=created-descending&filter.v.availability=1'

    # Chemin du fichier JSON
    json_file_path = 'produits_hikaru.json'

    while True :
        # Charger les données existantes du fichier JSON
        if os.path.exists(json_file_path):
            with open(json_file_path, 'r') as file:
                produits = json.load(file)
        else:
            produits = []

        # Envoyer une requête GET à la page
        response = requests.get(url)

        # Vérifier si la requête est réussie
        if response.status_code == 200:
            # Analyser le contenu de la page avec BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Trouver tous les conteneurs de produits
            product_containers = soup.find_all('product-card', class_='card card--product h-full card--no-lines relative flex')
            # Boucle pour extraire les informations de chaque produit
            for product in product_containers:
                # Extraire le titre du produit
                title = product.find('a', class_='card-link text-current js-prod-link').text.strip()
                
                # Extraire le prix du produit
                price = product.find('div', class_='price__default').text.strip()

                # Trouver la balise img
                image_tag = product.find('div', class_='card__media relative').find('img')
                img_url = 'https:' + image_tag['src'] if image_tag else None

                # Extraire le lien d'achat du produit
                link = product.find('a', class_='card-link text-current js-prod-link')['href']
                full_link = f'https://hikarudistribution.com{link}'

                # Extraction disponibilité
                # Envoyer une requête GET aux pages filles
                fille = requests.get(full_link)
                if fille.status_code == 200:
                    # Analyser le contenu de la page avec BeautifulSoup
                    soup_dispo = BeautifulSoup(fille.content, 'html.parser')
                    dispo = soup_dispo.find('div', class_='product-info__add-button').text.strip()
                else:
                    dispo = None
                
                # Créer un dictionnaire pour le produit
                produit = {
                    'title': title,
                    'price': price,
                    'image_url': img_url,
                    'link': full_link,
                    'dispo': dispo
                }

                # Vérifier si le produit est déjà dans le JSON
                found = False
                for existing_product in produits:
                    if existing_product['title'] == title and existing_product['price'] == price:
                        found = True
                        # Mettre à jour la disponibilité si elle a changé
                        if existing_product['dispo'] != dispo:
                            discord_webhook(
                                Webhook=Webhook,
                                title=f"hikaru \n{title}",
                                description=f"{title}. \nNouvelle disponibilité: {dispo}",
                                thumbnail=img_url,
                                url=full_link
                            )
                            existing_product['dispo'] = dispo
                        break

                # Si le produit n'est pas trouvé, l'ajouter au JSON et envoyer une notification
                if not found:
                    produits.append(produit)
                    discord_webhook(
                        Webhook=Webhook,
                        title=f"hikaru : \n{title}",
                        description=f"{title}.\nPrix: {price}\nDisponibilité: {dispo}",
                        thumbnail=img_url,
                        url=full_link
                    )

            # Enregistrer les données mises à jour dans le fichier JSON
            with open(json_file_path, 'w') as file:
                json.dump(produits, file, indent=4, ensure_ascii=False)

            print('Les informations des produits ont été mises à jour avec succès.')
        else:
            print('Erreur lors de la récupération de la page.')
        time.sleep(1)

def Pokeseller():
    # URL de la page à scraper
    Webhook = "https://discord.com/api/webhooks/1366093410208845834/ArVefJGAeESE86SU6U8Ljsi0wHmyfhygY7F9FqVZuVcjRB3g5r-FZoy_Wicp-Y6oMKML"
    url = 'https://www.pokeseller14.com/search?q=Pokemon&type=products&collections=Nouveaut%C3%A9+acceuil'

    # Chemin du fichier JSON
    json_file_path = 'produits_pokeseller.json'

    while True : 
        # Charger les données existantes du fichier JSON
        if os.path.exists(json_file_path):
            with open(json_file_path, 'r') as file:
                produits = json.load(file)
        else:
            produits = []

        # Envoyer une requête GET à la page
        response = requests.get(url)

        # Vérifier si la requête est réussie
        if response.status_code == 200:
            # Analyser le contenu de la page avec BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Trouver tous les conteneurs de produits
            product_containers = soup.find_all('li', class_='sERPSMg')
            
            # Boucle pour extraire les informations de chaque produit
            for product in product_containers:
                # Extraire le titre du produit
                title = product.find('div', class_='sJpr9vC').text.strip()
                
                # Extraire le prix du produit
                price = product.find('span', class_='sQq4biu').text.strip()

                # Trouver la balise img
                image_tag = product.find('img', class_='mS0yET heightByImageRatio heightByImageRatio2')
                img_url = 'https://www.pokeseller14.com' + image_tag['src'] if image_tag else None

                # Extraire le lien d'achat du produit
                link = product.find('a', class_='sil_d4M')['href']
                full_link = link
                # Extraction disponibilité
                # Envoyer une requête GET aux pages filles
                fille = requests.get(full_link)
                if fille.status_code == 200:
                    # Analyser le contenu de la page avec BeautifulSoup
                    soup_dispo = BeautifulSoup(fille.content, 'html.parser')
                    dispo = soup_dispo.find('span', class_='sZ3f0NI').text.strip()
                else:
                    dispo = None

                # Créer un dictionnaire pour le produit
                produit = {
                    'title': title,
                    'price': price,
                    'image_url': img_url,
                    'link': full_link,
                    'dispo': dispo
                }

                # Vérifier si le produit est déjà dans le JSON
                found = False
                for existing_product in produits:
                    if existing_product['title'] == title and existing_product['price'] == price:
                        found = True
                        # Mettre à jour la disponibilité si elle a changé
                        if existing_product['dispo'] != dispo:
                            discord_webhook(
                                Webhook=Webhook,
                                title=f"pokeseller14 \n{title}",
                                description=f"{title}. \nNouvelle disponibilité: {dispo}",
                                thumbnail=img_url,
                                url=full_link
                            )
                            existing_product['dispo'] = dispo
                        break

                # Si le produit n'est pas trouvé, l'ajouter au JSON et envoyer une notification
                if not found:
                    produits.append(produit)
                    discord_webhook(
                        Webhook=Webhook,
                        title=f"pokeseller14 : \n{title}",
                        description=f"{title}.\nPrix: {price}\nDisponibilité: {dispo}",
                        thumbnail=img_url,
                        url=full_link
                    )

            # Enregistrer les données mises à jour dans le fichier JSON
            try:
                with open(json_file_path, 'w', encoding='utf-8') as file:
                    json.dump(produits, file, indent=4, ensure_ascii=False)
                print('Les informations des produits ont été mises à jour avec succès.')
            except Exception as e:
                print(f"Erreur lors de la sauvegarde des données dans le fichier JSON : {e}")

        else:
            print('Erreur lors de la récupération de la page.')
        time.sleep(1)

def PokeGeek():
    # URL de la page à scraper
    Webhook = "https://discord.com/api/webhooks/1366093645878395045/7I1zbTjWwnIv_wawUZw_Z5wEfQOS8XtMwboHn6OmAYjLQkAP__aLcka2IPYfDpqLiXP3"
    url = 'https://www.poke-geek.fr/collections/produits-scelles-fr?sort_by=created-descending&filter.v.price.gte=&filter.v.price.lte='

    # Chemin du fichier JSON
    json_file_path = 'produits_pokegeek.json'

    while True:
        # Charger les données existantes du fichier JSON
        if os.path.exists(json_file_path):
            with open(json_file_path, 'r') as file:
                produits = json.load(file)
        else:
            produits = []

        # Envoyer une requête GET à la page
        response = requests.get(url)

        # Vérifier si la requête est réussie
        if response.status_code == 200:
            # Analyser le contenu de la page avec BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')

            # Trouver tous les conteneurs de produits
            product_containers = soup.find_all('div', class_='sf__col-item w-6/12 md:w-4/12 px-2 xl:px-3')

            # Boucle pour extraire les informations de chaque produit
            for product in product_containers:
                # Extraire le titre du produit
                title = product.find('h3', class_='block text-base').text.strip()

                # Extraire le prix du produit
                price = product.find('span', class_='f-price-item f-price-item--regular').text.strip()
                # Trouver la balise img
                image_tag = product.find('img', class_='se-out w-full h-full f-img-loaded')
                img_url = image_tag['src'] if image_tag else None

                # Extraire le lien d'achat du produit
                link = product.find('a', class_='block w-full')['href']
                full_link = f'https://www.poke-geek.fr{link}'

                # Extraction disponibilité
                # Envoyer une requête GET aux pages filles
                fille = requests.get(full_link)
                if fille.status_code == 200:
                    soup_dispo = BeautifulSoup(fille.content, 'html.parser')
                    dispo = soup_dispo.find('span', class_='not-change atc-text').text.strip()
                else:
                    dispo = None

                # Créer un dictionnaire pour le produit
                produit = {
                    'title': title,
                    'price': price,
                    'image_url': img_url,
                    'link': full_link,
                    'dispo': dispo
                }

                # Vérifier si le produit est déjà dans le JSON
                found = False
                for existing_product in produits:
                    if existing_product['title'] == title and existing_product['price'] == price:
                        found = True
                        # Mettre à jour la disponibilité si elle a changé
                        if existing_product['dispo'] != dispo:
                            discord_webhook(
                                Webhook=Webhook,
                                title=f"PokeGeek : \n{title}",
                                description=f"{title}. \nNouvelle disponibilité: {dispo}",
                                thumbnail=img_url,
                                url=full_link
                            )
                            existing_product['dispo'] = dispo
                        break

                # Si le produit n'est pas trouvé, l'ajouter au JSON et envoyer une notification
                if not found:
                    produits.append(produit)
                    discord_webhook(
                        Webhook=Webhook,
                        title=f"PokeGeek : \n{title}",
                        description=f"{title}.\nPrix: {price}\nDisponibilité: {dispo}",
                        thumbnail=img_url,
                        url=full_link
                    )

            # Enregistrer les données mises à jour dans le fichier JSON
            with open(json_file_path, 'w') as file:
                json.dump(produits, file, indent=4, ensure_ascii=False)

            print('Les informations des produits ont été mises à jour avec succès.')
        else:
            print('Erreur lors de la récupération de la page.')
        time.sleep(1)

def Pokito():
    # URL de la page à scraper
    Webhook = "https://discord.com/api/webhooks/1366093803139895346/jeW_bQNo3tJXA8Uc04YJzB0aPg9i8ln1p5mpfyjrjYEQKemlIVX_uKMRYrIu382oeJo2"
    url = 'https://www.pokito.fr/collections/produits-scelles?sort_by=best-selling&filter.v.availability=1'

    # Chemin du fichier JSON
    json_file_path = 'produits_pokito.json'

    while True : 
        # Charger les données existantes du fichier JSON
        if os.path.exists(json_file_path):
            with open(json_file_path, 'r') as file:
                produits = json.load(file)
        else:
            produits = []

        # Envoyer une requête GET à la page
        response = requests.get(url)

        # Vérifier si la requête est réussie
        if response.status_code == 200:
            # Analyser le contenu de la page avec BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Trouver tous les conteneurs de produits
            product_containers = soup.find_all('article', class_='product-column')  # Adapter la classe des conteneurs
            
            # Boucle pour extraire les informations de chaque produit
            for product in product_containers:
                # Extraire le titre du produit
                title = product.find('h3', class_='h6 product-column_heading mty').text.strip()  # Adapter la classe du titre
                
                # Extraire le prix du produit
                price = product.find('span', class_='regular-price main-price').text.strip()  # Adapter la classe du prix

                # Trouver la balise img
                image_tag = product.find('img', class_='product_gallery-item')  # Adapter la classe de l'image
                img_url = 'https://www.pokito.fr' + image_tag['src'] if image_tag else None

                # Extraire le lien d'achat du produit
                a_tag = product.find('a') # Extraire la valeur de l'attribut 'href' 
                href = a_tag['href'] 
                full_link = 'https://www.pokito.fr' + href

                dispo = product.find('button', class_='button button--product-action button--primary').text.strip()


                # Créer un dictionnaire pour le produit
                produit = {
                    'title': title,
                    'price': price,
                    'image_url': img_url,
                    'link': full_link,
                    'dispo': dispo
                }

                # Vérifier si le produit est déjà dans le JSON
                found = False
                for existing_product in produits:
                    if existing_product['title'] == title and existing_product['price'] == price:
                        found = True
                        # Mettre à jour la disponibilité si elle a changé
                        if existing_product['dispo'] != dispo:
                            discord_webhook(
                                Webhook=Webhook,
                                title=f"Poikito : \n{title}",
                                description=f"{title}. \nNouvelle disponibilité: {dispo}",
                                thumbnail=img_url,
                                url=full_link
                            )
                            existing_product['dispo'] = dispo
                        break

                # Si le produit n'est pas trouvé, l'ajouter au JSON et envoyer une notification
                if not found:
                    produits.append(produit)
                    discord_webhook(
                        Webhook=Webhook,
                        title=f"Pokito: \n{title}",
                        description=f"{title}.\nPrix: {price}\nDisponibilité: {dispo}",
                        thumbnail=img_url,
                        url=full_link
                    )

            # Enregistrer les données mises à jour dans le fichier JSON
            with open(json_file_path, 'w') as file:
                json.dump(produits, file, indent=4, ensure_ascii=False)

            print('Les informations des produits ont été mises à jour avec succès.')
        else:
            print('Erreur lors de la récupération de la page.')
        time.sleep(1)

def TradingCard() :
        # URL de la page à scraper
    Webhook = "https://discord.com/api/webhooks/1366094001987649686/3fvwJJ-AouHKKexV0dum8dpLd-uLVxScJnt62lXOiBQRqiOYP8XR91g3HCo73KpY5Gi5"
    url = 'https://www.tradingcard6107.fr/pokemon/newest-products'

    # Chemin du fichier JSON
    json_file_path = 'produits_TradingCard.json'

    while True :
        # Charger les données existantes du fichier JSON
        if os.path.exists(json_file_path):
            with open(json_file_path, 'r') as file:
                produits = json.load(file)
        else:
            produits = []

        # Envoyer une requête GET à la page
        response = requests.get(url)

        # Vérifier si la requête est réussie
        if response.status_code == 200:
            # Analyser le contenu de la page avec BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Trouver tous les conteneurs de produits
            product_containers = soup.find_all('div', class_='prod__shadow')  # Adapter la classe des conteneurs
            
            # Boucle pour extraire les informations de chaque produit
            for product in product_containers:
                # Extraire le titre du produit
                title = product.find('span', class_='prod__name__title').text.strip()  # Adapter la classe du titre
                # Extraire le prix du produit
                price = product.find('div', class_='prod__price').text.strip()  # Adapter la classe du prix

                # Trouver la balise img
                image_tag = product.find('img', class_='product_gallery-item')  # Adapter la classe de l'image
                img_url = 'https://www.tradingcard6107.fr' + image_tag['src'] if image_tag else None

                # Extraire le lien d'achat du produit
                a_tag = product.find('a') # Extraire la valeur de l'attribut 'href' 
                href = a_tag['href'] 
                full_link = 'https://www.tradingcard6107.fr' + href

                fille = requests.get(full_link)
                if fille.status_code == 200:
                    # Analyser le contenu de la page avec BeautifulSoup
                    soup_dispo = BeautifulSoup(fille.content, 'html.parser')
                    dispo = soup_dispo.find('span', class_='c1-button').text.strip()
                else:
                    dispo = None


                # Créer un dictionnaire pour le produit
                produit = {
                    'title': title,
                    'price': price,
                    'image_url': img_url,
                    'link': full_link,
                    'dispo': dispo
                }

                # Vérifier si le produit est déjà dans le JSON
                found = False
                for existing_product in produits:
                    if existing_product['title'] == title and existing_product['price'] == price:
                        found = True
                        # Mettre à jour la disponibilité si elle a changé
                        if existing_product['dispo'] != dispo:
                            discord_webhook(
                                Webhook=Webhook,
                                title=f"TradingCard : \n{title}",
                                description=f"{title}. \nNouvelle disponibilité: {dispo}",
                                thumbnail=img_url,
                                url=full_link
                            )
                            existing_product['dispo'] = dispo
                        break

                # Si le produit n'est pas trouvé, l'ajouter au JSON et envoyer une notification
                if not found:
                    produits.append(produit)
                    discord_webhook(
                        Webhook=Webhook,
                        title=f"TradingCard : \n{title}",
                        description=f"{title}.\nPrix: {price}\nDisponibilité: {dispo}",
                        thumbnail=img_url,
                        url=full_link
                    )

            # Enregistrer les données mises à jour dans le fichier JSON
            with open(json_file_path, 'w') as file:
                json.dump(produits, file, indent=4, ensure_ascii=False)

            print('Les informations des produits ont été mises à jour avec succès.')
        else:
            print('Erreur lors de la récupération de la page.')
        time.sleep(1)

def lacitedesnuages() :
        # URL de la page à scraper
    Webhook = "https://discord.com/api/webhooks/1366094187967283341/8ElHqqBCfzD6RlTrkckrgVdx8e3m7V-T5aJKWqLZSxgl3_Y_WrqSllz1FquTUcH8r-uH"
    url = 'https://www.lacitedesnuages.be/fr/604-pokemon/s-1/etat-en_stock/types_de_produit-jcc_jeux_de_cartes_a_collectionner/licence-pokemon?order=product.date_upd.desc'

    # Chemin du fichier JSON
    json_file_path = 'produits_lacitedesnuages.json'

    while True :
        # Charger les données existantes du fichier JSON
        if os.path.exists(json_file_path):
            with open(json_file_path, 'r') as file:
                produits = json.load(file)
        else:
            produits = []

        # Envoyer une requête GET à la page
        response = requests.get(url)

        # Vérifier si la requête est réussie
        if response.status_code == 200:
            # Analyser le contenu de la page avec BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Trouver tous les conteneurs de produits
            product_containers = soup.find_all('div', class_='product-miniature-wrapper')  # Adapter la classe des conteneurs
            
            # Boucle pour extraire les informations de chaque produit
            for product in product_containers:
                # Extraire le titre du produit
                title = product.find('div', class_='h3 product-title').text.strip()  # Adapter la classe du titre
                # Extraire le prix du produit
                price = product.find('div', class_='product-price-and-shipping').text.strip()  # Adapter la classe du prix

                # Trouver la balise img
                image_tag = product.find('img', class_='img-fluid')  # Adapter la classe de l'image
                img_url = image_tag['src'] if image_tag else None

                # Extraire le lien d'achat du produit
                a_tag = product.find('a') # Extraire la valeur de l'attribut 'href' 
                href = a_tag['href'] 
                full_link = href

                dispo = product.find('ul', class_='product-flags').text.strip()

                # Créer un dictionnaire pour le produit
                produit = {
                    'title': title,
                    'price': price,
                    'image_url': img_url,
                    'link': full_link,
                    'dispo': dispo
                }

                # Vérifier si le produit est déjà dans le JSON
                found = False
                for existing_product in produits:
                    if existing_product['title'] == title and existing_product['price'] == price:
                        found = True
                        # Mettre à jour la disponibilité si elle a changé
                        if existing_product['dispo'] != dispo:
                            discord_webhook(
                                Webhook=Webhook,
                                title=f"lacitedesnuages : \n{title}",
                                description=f"{title}. \nNouvelle disponibilité: {dispo}",
                                thumbnail=img_url,
                                url=full_link
                            )
                            existing_product['dispo'] = dispo
                        break

                # Si le produit n'est pas trouvé, l'ajouter au JSON et envoyer une notification
                if not found:
                    produits.append(produit)
                    discord_webhook(
                        Webhook=Webhook,
                        title=f"lacitedesnuages : \n{title}",
                        description=f"{title}.\nPrix: {price}\nDisponibilité: {dispo}",
                        thumbnail=img_url,
                        url=full_link
                    )

            # Enregistrer les données mises à jour dans le fichier JSON
            with open(json_file_path, 'w') as file:
                json.dump(produits, file, indent=4, ensure_ascii=False)

            print('Les informations des produits ont été mises à jour avec succès.')
        else:
            print('Erreur lors de la récupération de la page.')
        time.sleep(1)

def pokemael():
    # URL de la page à scraper
    Webhook = "https://discord.com/api/webhooks/1328823263886970901/A_S5lEhhfhKk9DsfQTEgBBWjgQ2jYYmODiee0lbbB1K5w3ZJJdExD5D313ZB8GfrIZe1"
    url = 'https://pokemael.com/collections/scelle?filter.v.availability=1&filter.v.price.gte=&filter.v.price.lte=&sort_by=created-descending'
    # Chemin du fichier JSON
    json_file_path = 'produits_pokemael.json'

    while True : 
        # Charger les données existantes du fichier JSON
        if os.path.exists(json_file_path):
            with open(json_file_path, 'r') as file:
                produits = json.load(file)
        else:
            produits = []

        # Envoyer une requête GET à la page
        response = requests.get(url)
        # Vérifier si la requête est réussie
        if response.status_code == 200:
            # Analyser le contenu de la page avec BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Trouver tous les conteneurs de produits
            product_containers = soup.find_all('li', class_='grid__item scroll-trigger animate--slide-in')
            
            # Boucle pour extraire les informations de chaque produit
            for product in product_containers:
                # Extraire le titre du produit
                title = product.find('h3', class_='card__heading h5').text.strip()
                
                # Extraire le prix du produit
                price = product.find('span', class_='price-item price-item--regular').text.strip()

                # Trouver la balise img
                image_tag = product.find('img', class_='motion-reduce')
                img_url = image_tag['src'] if image_tag else None

                # Extraire le lien d'achat du produit
                link = product.find('a', class_='full-unstyled-link')['href']
                full_link = f'https://pokemael.com{link}'

                # Extraction disponibilité
                # Envoyer une requête GET aux pages filles
                fille = requests.get(full_link)
                if fille.status_code == 200:
                    # Analyser le contenu de la page avec BeautifulSoup
                    soup_dispo = BeautifulSoup(fille.content, 'html.parser')
                    dispo = soup_dispo.find('div', class_='product-form__buttons').text.strip()
                else:
                    dispo = "Non spécifié"

                # Validation des données
                if len(title) > 256:
                    title = title[:253] + "..."
                if len(price) > 2048:
                    price = price[:2045] + "..."
                if not img_url or not img_url.startswith("http"):
                    img_url = None
                if not full_link or not full_link.startswith("http"):
                    full_link = None

                produit = {
                    'title': title,
                    'price': price,
                    'image_url': img_url,
                    'link': full_link,
                    'dispo': dispo
                }

                # Vérifier si le produit est déjà dans le JSON
                found = False
                for existing_product in produits:
                    if existing_product['title'] == title and existing_product['price'] == price:
                        found = True
                        if existing_product['dispo'] != dispo:
                            discord_webhook(
                                Webhook=Webhook,
                                title=f"PokeMael \n{title}",
                                description=f"{title}. \nNouvelle disponibilité: {dispo}",
                                thumbnail=img_url,
                                url=full_link
                            )
                            existing_product['dispo'] = dispo
                        break

                if not found:
                    produits.append(produit)
                    discord_webhook(
                        Webhook=Webhook,
                        title=f"PokeMael : \n{title}",
                        description=f"{title}.\nPrix: {price}\nDisponibilité: {dispo}",
                        thumbnail=img_url,
                        url=full_link
                    )

            # Enregistrer les données mises à jour dans le fichier JSON
            with open(json_file_path, 'w') as file:
                json.dump(produits, file, indent=4, ensure_ascii=False)

            print('Les informations des produits ont été mises à jour avec succès.')
        else:
            print('Erreur lors de la récupération de la page.')
        time.sleep(1)

# Création des threads
thread1 = threading.Thread(target=TradingCard)
thread2 = threading.Thread(target=TCGspeed)
thread3 = threading.Thread(target=Pokito)
thread4 = threading.Thread(target=Hikaru)
thread5 = threading.Thread(target=Pokeseller)
thread6 = threading.Thread(target=lacitedesnuages)
thread7 = threading.Thread(target=pokemael)
thread8 = threading.Thread(target=PokeGeek)

# Démarrage des threads
thread1.start()
thread2.start()
thread3.start()
thread4.start()
thread5.start()
thread6.start()
thread7.start()
thread8.start()

# Attendre que tous les threads se terminent
thread1.join()
thread2.join()
thread3.join()
thread4.join()
thread5.join()
thread6.join()
thread7.join()
thread8.join()
