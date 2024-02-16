import requests
import random
from bs4 import BeautifulSoup

# Liste des proxies (remplacez ceci avec vos propres proxies)
proxies = [
    "117.250.3.58:8080",
]


def get_random_proxy(proxies):
    """ Sélectionne un proxy aléatoire de la liste """
    random_proxy = random.choice(proxies)
    return {"http": f"http://{random_proxy}", "https": f"https://{random_proxy}"}


def scrape_site(url, proxies):
    """ Scraper un site en utilisant un proxy rotatif """
    try:
        print("Scraping", url)
        proxy = get_random_proxy(proxies)
        response = requests.get(url, proxies=proxy)
        return response.text
    except requests.exceptions.ProxyError:
        print("Erreur de proxy, en essayant un autre...")
        return scrape_site(url, proxies)


# Exemple d'utilisation
url = 'http://127.0.0.1:8080/scraping/'  # Remplacez avec l'URL que vous voulez scraper
page_content = scrape_site(url, proxies)
soup = BeautifulSoup(page_content, 'html.parser')
print(soup.select_one("h1"))
