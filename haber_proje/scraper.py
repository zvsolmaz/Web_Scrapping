import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from urllib.parse import urljoin

# MongoDB bağlantı
client = MongoClient("mongodb://localhost:27017/")
db = client["haber_db"]
collection = db["haberler"]

BASE_URL = "https://www.cagdaskocaeli.com.tr/"

# siteyi çek
response = requests.get(BASE_URL)
soup = BeautifulSoup(response.text, "html.parser")

# tüm linkleri bul
links = soup.find_all("a")

for link in links:
    href = link.get("href")

    if not href:
        continue

    # sadece haber linkleri
    if "/haber/" not in href:
        continue

    # 🔥 doğru link oluşturma (en sağlam yöntem)
    full_link = urljoin(BASE_URL, href)

    # duplicate kontrol
    if collection.find_one({"link": full_link}):
        continue

    try:
        detail = requests.get(full_link)
        detail_soup = BeautifulSoup(detail.text, "html.parser")

        # başlık
        title_tag = detail_soup.find("h1")
        title = title_tag.text.strip() if title_tag else "Başlık yok"

        # içerik (tüm p taglerini birleştir)
        paragraphs = detail_soup.find_all("p")
        content = " ".join([p.text.strip() for p in paragraphs])

        data = {
            "title": title,
            "content": content,
            "link": full_link,
            "source": "cagdaskocaeli"
        }

        collection.insert_one(data)
        print("Eklendi:", title)

    except Exception as e:
        print("Hata:", full_link)
        print(e)