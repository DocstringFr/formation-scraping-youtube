import re
from bs4 import BeautifulSoup


def get_average_price(html: str) -> int:
    """From the HTML, we get the average price"""

    prices = []

    soup = BeautifulSoup(html, 'html.parser')
    divs = soup.find_all('div', {'data-testid': "card-container"})

    for div in divs:
        price_div = div.find('span', class_="_1y74zjx") or div.find('span', class_="_tyxjp1")
        if not price_div:
            continue

        price = re.sub(r"\D", "", price_div.text)
        if price.isdigit():
            prices.append(int(price))

    return round(sum(prices) / len(prices)) if len(prices) else 0
