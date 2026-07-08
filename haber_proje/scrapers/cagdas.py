import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from utils.ssl_session import make_session, safe_get
from config import BASE_SOURCES
from preprocess import clean_text, clean_url
from classifier import classify_news
from date_utils import parse_turkish_date, is_within_last_3_days

BASE_URL = BASE_SOURCES["cagdaskocaeli"]
SCRAPE_URL = BASE_URL

KOCAELI_ILCELER = {
    "darica": "Darıca", "basiskele": "Başiskele",
    "golcuk": "Gölcük", "korfez": "Körfez",
    "kandira": "Kandıra", "dilovasi": "Dilovası",
    "karamursel": "Karamürsel", "cayirova": "Çayırova",
    "izmit": "İzmit", "kocaeli": "Kocaeli",
    "gebze": "Gebze", "kartepe": "Kartepe",
    "derince": "Derince"
}


def turkce_norm(metin: str) -> str:
    return (
        metin
        .replace("İ", "i").replace("I", "ı")
        .replace("Ğ", "ğ").replace("Ü", "ü")
        .replace("Ş", "ş").replace("Ö", "ö")
        .replace("Ç", "ç")
        .lower()
        .replace("ı", "i").replace("ğ", "g")
        .replace("ü", "u").replace("ş", "s")
        .replace("ö", "o").replace("ç", "c")
    )


def ilce_bul(metin: str) -> str | None:
    metin_norm = turkce_norm(metin)
    # Son 100 karakteri çıkar — ajans/muhabir bilgisi orada olur
    metin_norm = metin_norm[:-100] if len(metin_norm) > 100 else metin_norm

    en_erken_pos = len(metin_norm) + 1
    bulunan = None
    for ilce_ascii, ilce_turkce in KOCAELI_ILCELER.items():
        if ilce_ascii == "kocaeli":
            continue
        pos = metin_norm.find(ilce_ascii)
        if pos != -1 and pos < en_erken_pos:
            en_erken_pos = pos
            bulunan = ilce_turkce

    # "kocaeli" son çare — sadece başlık + ilk 150 karakterde geçiyorsa al
    if not bulunan:
        ilk_kisim = turkce_norm(metin)[:150]
        if "kocaeli" in ilk_kisim:
            bulunan = "Kocaeli"

    return bulunan

def fetch_cagdas_news():
    results = []
    session = make_session()

    response = safe_get(SCRAPE_URL, session=session)
    if response is None:
        print("cagdaskocaeli ana sayfa hatası: bağlantı kurulamadı")
        return results

    soup = BeautifulSoup(response.text, "html.parser")
    seen_links = set()

    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]

        if "/haber/" not in href:
            continue

        full_link = urljoin(BASE_URL, href)
        clean_link = clean_url(full_link)

        if clean_link in seen_links:
            continue
        seen_links.add(clean_link)

        time.sleep(1)

        try:
            detail_response = safe_get(full_link, session=session)
            if detail_response is None:
                print(f"Detay hatası {full_link}: bağlantı kurulamadı")
                continue

            detail_soup = BeautifulSoup(detail_response.text, "html.parser")

            h1 = detail_soup.find("h1")
            title = clean_text(h1.get_text()) if h1 else ""
            if not title:
                continue

            paragraphs = detail_soup.find_all("p")
            content = clean_text(" ".join(p.get_text() for p in paragraphs))
            if len(content) < 80:
                continue

            published_at = None
            time_tag = detail_soup.find("time")
            if time_tag:
                raw = time_tag.get("datetime") or time_tag.get_text()
                published_at = parse_turkish_date(raw)
            if not published_at:
                meta = detail_soup.find("meta", property="article:published_time")
                if meta:
                    published_at = parse_turkish_date(meta.get("content", ""))
            if not published_at:
                for sel in [".tarih", ".date", ".publish-date", ".news-date"]:
                    el = detail_soup.select_one(sel)
                    if el:
                        published_at = parse_turkish_date(el.get_text())
                        if published_at:
                            break

            if published_at and not is_within_last_3_days(published_at):
                print(f"⏭ Eski haber ({published_at.date()}): {title[:50]}")
                continue

            haber_turu = classify_news(title, content)
            if haber_turu is None:
                print(f"🏷 Kategori dışı: {title[:60]}")
                continue

            ilce = ilce_bul(title + " " + content)
            results.append({
                "title": title,
                "content_raw": content,
                "link": clean_link,
                "source": "cagdaskocaeli",
                "haber_turu": haber_turu,
                "ilce": ilce,
                "published_at": published_at,
                "published_at_raw": None,
                "raw_location_text": None,
            })
            print(f"✅ [{haber_turu}] [{ilce or '?'}] {title[:55]}")

        except Exception as e:
            print(f"Detay hatası {full_link}: {e}")

    print(f"\nToplam çekilen: {len(results)}")
    return results