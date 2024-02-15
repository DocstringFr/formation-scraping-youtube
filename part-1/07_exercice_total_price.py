import re
import sys
from typing import List
from urllib.parse import urljoin

import requests
from loguru import logger
from selectolax.parser import HTMLParser

logger.remove()
logger.add(f'books.log',
           level="WARNING",
           rotation="500kb")

logger.add(sys.stderr, level="INFO")

BASE_URL = "https://books.toscrape.com/"


def get_book_price_from_url(url: str, session: requests.Session = None) -> float:
    """
    Récupère le prix d'un livre à partir de son URL.

    :param url: URL de la page du livre
    :param session: Session HTTP pour effectuer les requêtes
    :return: Prix du livre
    """

    try:
        if session:
            response = session.get(url)
        else:
            response = requests.get(url)

        response.raise_for_status()  # Vérifie que la requête a réussi

        tree = HTMLParser(response.text)
        price = extract_price_from_page(tree)
        stock = extract_stock_quantity_from_page(tree)
        return price * stock
    except requests.exceptions.RequestException as e:
        logger.error(f"Erreur lors de la requête HTTP : {e}")
        return 0.0
    except Exception as e:
        logger.error(f"Erreur lors de l'extraction du prix depuis l'URL : {e}")
        return 0.0


def extract_price_from_page(tree: HTMLParser) -> float:
    """
    Extrait le prix d'un livre depuis la page du livre.

    :param tree: HTMLParser object de la page du livre
    :return: Prix du livre
    """

    price_node = tree.css_first("p.price_color")

    if price_node:
        price_string = price_node.text()
    else:
        logger.error("Aucun noeud n'a été trouvé")
        return 0.0

    try:
        price = re.findall(r"[0-9.]+", price_string)[0]
    except IndexError as e:
        logger.error(f"Aucun nombre n'a été trouvé : {e}")
        return 0.0
    else:
        return float(price)


def extract_stock_quantity_from_page(tree: HTMLParser) -> int:
    """
    Extrait la quantité de livres en stock sur la page du livre.

    :param tree: HTMLParser object de la page du livre
    :return: Quantité de livres en stock
    """

    try:
        price_node = tree.css_first("p.instock.availability")
        return int(re.findall(r"\d+", price_node.text())[0])
    except AttributeError:
        logger.error("Aucun noeud 'p.instock.availability' n'a été trouvé")
        return 0
    except IndexError:
        logger.error("Aucun nombre trouvé dans le texte de 'p.instock.availability'")
        return 0


def get_next_page_url(url: str, tree: HTMLParser) -> str | None:
    """
    Récupère l'URL de la page suivante à partir d'une page donnée.

    :param url: URL de la page actuelle
    :param tree: HTMLParser object de la page actuelle
    :return: URL de la page suivante
    """

    next_page_node = tree.css_first("li.next > a")
    if next_page_node and "href" in next_page_node.attributes:
        next_page_link = next_page_node.attributes.get("href")
        return urljoin(url, next_page_link)

    logger.debug(f"Couldn't find next page URL")
    return None


def get_all_books_urls_on_page(url: str, tree: HTMLParser) -> List[str]:
    """
    Récupère toutes les URLs des livres présents sur une page.

    :param url: URL de la page
    :param tree: HTMLParser object de la page
    :return: Liste des URLs des livres
    """

    try:
        book_links = tree.css('h3 > a')
        urls = [urljoin(url, link.attributes.get('href')) for link in book_links if 'href' in link.attributes]
        return urls
    except Exception as e:
        logger.error(f"Erreur lors de l'extraction des URLs des livres sur la page {url} : {e}")
        return []


def get_all_books_urls(url: str) -> List[str]:
    """
    Récupère toutes les URLs des livres sur toutes les pages à partir d'une URL de départ.

    :param url: URL de départ
    :return: Liste de toutes les URLs des livres
    """

    urls = []

    with requests.Session() as session:
        while True:
            try:
                logger.info(f"Scraping page {url}")
                r = session.get(url)
                r.raise_for_status()
            except requests.RequestException as e:
                logger.error(f"Erreur lors de la requête HTTP sur la page {url} : {e}")
                continue

            tree = HTMLParser(r.text)
            books_urls = get_all_books_urls_on_page(url, tree)
            urls.extend(books_urls)

            url = get_next_page_url(url, tree)
            if not url:
                break

    return urls


def get_total_price_of_all_books(urls: list) -> float:
    """
    Calcule le prix total de tous les livres (prix * quantité en stock) sur toutes les pages à partir d'une URL de départ.

    :param urls: URLs à scrapper
    :return: Prix total de tous les livres
    """

    total_price = 0.0
    with requests.Session() as session:
        for url in urls:
            logger.info(f"Scraping book {url}")
            total_price += get_book_price_from_url(url, session=session)
        return total_price


def main():
    urls = get_all_books_urls(BASE_URL)
    total_price = get_total_price_of_all_books(urls)
    print(f"Total price of all books is {total_price}")


if __name__ == '__main__':
    main()
