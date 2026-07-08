import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from config import BASE_SOURCES
from preprocess import clean_text, clean_url
from classifier import classify_news
from date_utils import parse_turkish_date, is_within_last_3_days
from utils.ssl_session import make_session, safe_get

BASE_URL = BASE_SOURCES["seskocaeli"]

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

def fetch_ses_news():
    results = []
    session = make_session()

    # Ana sayfa — SSL hatası olabilir, safe_get kullan
    response = safe_get(BASE_URL, session=session)
    if response is None:
        print("seskocaeli ana sayfa hatası: bağlantı kurulamadı (SSL dahil)")
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

        # Detay sayfası — safe_get ile SSL-toleranslı çek
        r = safe_get(full_link, session=session)
        if r is None:
            print(f"Detay hatası {full_link}: bağlantı kurulamadı")
            continue

        try:
            soup2 = BeautifulSoup(r.text, "html.parser")

            h1 = soup2.find("h1")
            title = clean_text(h1.get_text()) if h1 else ""
            if not title:
                continue

            paragraphs = soup2.find_all("p")
            content = clean_text(" ".join(p.get_text() for p in paragraphs))
            if len(content) < 80:
                continue

            published_at = None
            for sel in [".tarih", ".date", ".publish-date", ".news-date"]:
                el = soup2.select_one(sel)
                if el:
                    published_at = parse_turkish_date(el.get_text())
                    if published_at:
                        break
            if not published_at:
                time_tag = soup2.find("time")
                if time_tag:
                    published_at = parse_turkish_date(
                        time_tag.get("datetime") or time_tag.get_text()
                    )
            if not published_at:
                meta = soup2.find("meta", property="article:published_time")
                if meta:
                    published_at = parse_turkish_date(meta.get("content", ""))

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
                "source": "seskocaeli",
                "haber_turu": haber_turu,
                "ilce": ilce,
                "published_at": published_at,
                "published_at_raw": None,
                "raw_location_text": None,
            })
            print(f"✅ [{haber_turu}] [{ilce or '?'}] {title[:55]}")

        except Exception as e:
            print(f"Detay hatası {full_link}: {e}")

    print(f"\nseskocaeli toplam: {len(results)}")
    return results
