import requests
from bs4 import BeautifulSoup

response = requests.get("https://books.toscrape.com/index.html")
soup = BeautifulSoup(response.text, "html.parser")

articles = soup.find_all("article", class_="product_pod")
for article in articles:
    links = article.find_all("a")
    if len(links) >= 2:
        link = links[1]
        print(link.get('title'))

titles = [a['title'] for a in soup.find_all('a', title=True)]
print(titles)
