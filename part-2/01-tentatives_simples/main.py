import re
import logging

import requests
from requests.exceptions import RequestException

from bs4 import BeautifulSoup
from pathlib import Path

FILEPATH = Path(__file__).parent / "airbnb.html"
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARNING)


def fetch_content(url: str, from_disk: bool = False) -> str:
    """Fetch the content of the page"""

    if from_disk and FILEPATH.exists():
        return _read_from_file()

    try:
        logger.debug(f"Making request to {url}")
        response = requests.get(url)
        response.raise_for_status()
        html_content = response.text
        _write_to_file(content=html_content)
        return html_content
    except RequestException as e:
        logger.error(f"Couldn't fetch content from {url} due to {str(e)}")
        raise e


def _write_to_file(content: str) -> bool:
    """Write content to file"""
    logger.debug("Writing content to file")
    with open(FILEPATH, "w") as f:
        f.write(content)

    return FILEPATH.exists()


def _read_from_file() -> str:
    """Read content from file"""
    logger.debug("Reading content from file")

    with open(FILEPATH, "r") as f:
        return f.read()


def get_average_price(html: str) -> int:
    """From the soup, we get the average price for the month"""
    prices = []

    soup = BeautifulSoup(html, 'html.parser')
    divs = soup.find_all('div', itemprop="itemListElement")
    for div in divs:
        price = div.find("span", class_="_tyxjp1") or div.find("span", class_="_1y74zjx")
        if not price:
            logger.warning(f"Couldn't find price in {div}")
            continue

        price = re.sub(r"\D", "", price.text)
        if price.isdigit():
            logger.debug(f"Price found : {price}")
            prices.append(int(price))
        else:
            logger.warning(f"Price {price} is not a digit")

    return round(sum(prices) / len(prices)) if len(prices) else 0


if __name__ == '__main__':
    url = "https://www.airbnb.fr/s/Rio-de-Janeiro--Rio-de-Janeiro--Br%C3%A9sil/homes?tab_id=home_tab&monthly_start_date=2024-01-01&monthly_length=3&price_filter_input_type=0&channel=EXPLORE&query=Rio%20de%20Janeiro,%20Br%C3%A9sil&date_picker_type=flexible_dates&flexible_trip_dates%5B%5D=january&flexible_trip_lengths%5B%5D=one_month&adults=1&source=structured_search_input_header&search_type=autocomplete_click&price_filter_num_nights=28&place_id=ChIJW6AIkVXemwARTtIvZ2xC3FA"
    html_content = fetch_content(url, from_disk=True)
    print(get_average_price(html_content))
