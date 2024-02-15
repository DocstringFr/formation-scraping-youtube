import re

import requests
from bs4 import BeautifulSoup


def main():
    response = requests.get("https://books.toscrape.com/index.html")
    soup = BeautifulSoup(response.text, 'html.parser')

    one_star_books = soup.select(".star-rating.One")
    for book in one_star_books:
        try:
            book_link = book.find_next("h3").find("a")["href"]
        except AttributeError as e:
            print("Impossible de trouver la balise h3 ou a.")
            raise AttributeError from e
        except KeyError as e:
            print("Impossible de trouver l'attribut href.")
            raise KeyError from e

        try:
            book_id = re.findall(r"_\d+", book_link)[0][1:]
            print(f"ID du livre à enlever : {book_id}")
        except IndexError as e:
            print("Impossible de trouver l'ID du livre.")
            raise IndexError from e


if __name__ == '__main__':
    main()
