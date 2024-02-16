import os
import sys
from datetime import datetime
from pathlib import Path
import json
import urllib3

import requests
from selectolax.parser import HTMLParser
from dotenv import load_dotenv
from loguru import logger
import sentry_sdk

sentry_sdk.init(
    dsn=os.environ["PUSHOVER_USER"],
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
)

load_dotenv()

PRICE_FILEPATH = Path(__file__).parent / "price.json"

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger.remove()
logger.add(sys.stderr, level="DEBUG")
logger.add("logs/debug.log", level="WARNING", rotation="1 MB")


def write_price_to_file(price: int):
    logger.info(f"Writing price {price} to file")

    if PRICE_FILEPATH.exists():
        with open(PRICE_FILEPATH, "r") as f:
            data = json.load(f)
    else:
        data = []

    data.append(
        {
            "price": price,
            "timestamp": datetime.now().isoformat()
        }
    )

    with open(PRICE_FILEPATH, "w") as f:
        json.dump(data, f, indent=4)


def get_price_difference(current_price: int) -> int:
    logger.info("Getting price difference")

    if PRICE_FILEPATH.exists():
        with open(PRICE_FILEPATH, "r") as f:
            data = json.load(f)

        previous_price = data[-1]["price"]
    else:
        previous_price = current_price

    try:
        return round((previous_price - current_price) / previous_price * 100)
    except ZeroDivisionError as e:
        logger.error("La variable previous_price contient la valeur 0 : divion impossible")
        raise e


def send_alert(message):
    logger.info(f"Sending alert with message {message}")

    try:
        response = requests.post("https://api.pushover.net/1/messages.json",
                                 data={"token": os.environ["PUSHOVER_TOKEN"],
                                       "user": os.environ["PUSHOVER_USER"],
                                       "message": message}
                                 )
        response.raise_for_status()

    except requests.RequestException as e:
        logger.error(f"Couldn't send alert due to {str(e)}")
        raise e


def get_current_price(asin: str):
    proxies = {
        "http": os.environ["PROXY"],
        "https": os.environ["PROXY"],
    }

    url = f"https://www.amazon.co.uk/dp/{asin}"

    try:
        response = requests.get(url, proxies=proxies, verify=False)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Couldn't fetch content from {url} due to {str(e)}")
        raise e

    html_content = response.text
    tree = HTMLParser(html_content)
    price_node = tree.css_first("span.a-price-whole")
    if price_node:
        return int(price_node.text().replace(".", ""))

    error_msg = f"Couldn't find price in {url}"
    logger.error(error_msg)
    raise ValueError(error_msg)


def main(asin: str):
    current_price = get_current_price(asin=asin)
    price_difference = get_price_difference(current_price=current_price)
    write_price_to_file(price=current_price)

    if price_difference > 0:
        send_alert(f"Price has decreased by {price_difference}%")


if __name__ == '__main__':
    asin = "B09R9L6J71"
    main(asin)
