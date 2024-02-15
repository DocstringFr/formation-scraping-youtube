from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://books.toscrape.com/index.html"


def main(threshold: int = 5):
    with requests.Session() as session:
        response = session.get(BASE_URL)

        soup = BeautifulSoup(response.text, 'html.parser')
        categories = soup.find('ul', class_="nav nav-list").find_all('a')

        # Alternative
        categories = soup.select('ul.nav.nav-list a')
        categories_urls = [category['href'] for category in categories]

        # Go to all categories page
        for category_url in categories_urls:
            full_url = urljoin(BASE_URL, category_url)
            response = session.get(full_url)
            soup = BeautifulSoup(response.text, 'html.parser')

            books = soup.find_all('article', class_="product_pod")
            books = soup.select('article.product_pod')
            category_title = soup.find("h1").text
            number_of_books = len(books)
            if number_of_books <= threshold:
                print(f"La catégorie '{category_title}' ne contient pas assez de livres ({number_of_books})")


if __name__ == '__main__':
    main(threshold=5)
