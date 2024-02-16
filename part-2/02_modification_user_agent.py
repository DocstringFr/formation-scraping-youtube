import requests

user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
headers = {"User-Agent": user_agent}
r = requests.get("https://www.docstring.fr/scraping/api/books/", headers=headers)
print(r.json())
