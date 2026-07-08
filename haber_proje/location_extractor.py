"""
Konum Çıkarımı ve Geocoding Modülü
- Haber metninden ilçe/mahalle/sokak bilgisi çıkarır
- Google Geocoding API ile enlem/boylam bulur
- Sonuçları önbellekte saklar (gereksiz API çağrısı önlenir)
"""

import re
import time
import requests
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_GEOCODING_API_KEY")
GOOGLE_GEOCODING_URL = "https://maps.googleapis.com/maps/api/geocode/json"

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["haber_db"]
cache_col = db["konum_cache"]

ILCELER = {
    "izmit": "İzmit",
    "gebze": "Gebze",
    "darica": "Darıca",
    "kartepe": "Kartepe",
    "basiskele": "Başiskele",
    "golcuk": "Gölcük",
    "korfez": "Körfez",
    "derince": "Derince",
    "kandira": "Kandıra",
    "dilovasi": "Dilovası",
    "karamursel": "Karamürsel",
    "cayirova": "Çayırova",
}

ILCE_KOORDINATLARI = {
    "İzmit":      (40.7654, 29.9408),
    "Gebze":      (40.8024, 29.4309),
    "Darıca":     (40.7667, 29.3667),
    "Kartepe":    (40.6833, 29.9167),
    "Başiskele":  (40.7167, 29.8833),
    "Gölcük":     (40.6500, 29.8167),
    "Körfez":     (40.7667, 29.7833),
    "Derince":    (40.7333, 29.8167),
    "Kandıra":    (41.0667, 30.1500),
    "Dilovası":   (40.7833, 29.5167),
    "Karamürsel": (40.6833, 29.6167),
    "Çayırova":   (40.8000, 29.3667),
    "Kocaeli":    (40.7654, 29.9408),
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


def konum_cikar(baslik: str, icerik: str) -> dict | None:
    baslik_norm = turkce_norm(baslik)
    icerik_norm = turkce_norm(icerik)

    sonuc = {
        "metin": None,
        "ilce": None,
        "mahalle": None,
        "sokak": None,
        "enlem": None,
        "boylam": None
    }

    parcalar = []
    tam_metin = baslik + " " + icerik

    # 1. İlçe tespiti — başlıkta ilk geçen ilçeyi bul
    en_erken_pos = len(baslik_norm) + 1
    bulunan_ilce = None

    for ilce_ascii, ilce_turkce in ILCELER.items():
        pos = baslik_norm.find(ilce_ascii)
        if pos != -1 and pos < en_erken_pos:
            en_erken_pos = pos
            bulunan_ilce = ilce_turkce

    # Başlıkta bulunamadıysa içerikte ilk geçeni bul
    if not bulunan_ilce:
        en_erken_pos = len(icerik_norm) + 1
        for ilce_ascii, ilce_turkce in ILCELER.items():
            pos = icerik_norm.find(ilce_ascii)
            if pos != -1 and pos < en_erken_pos:
                en_erken_pos = pos
                bulunan_ilce = ilce_turkce

    # TEM geçişi → ilçe bulunamadıysa İzmit fallback
    if not bulunan_ilce:
        if re.search(r'\bTEM\b', tam_metin):
            bulunan_ilce = "İzmit"

    if bulunan_ilce:
        sonuc["ilce"] = bulunan_ilce
        parcalar.append(bulunan_ilce)

    # 2. Mahalle tespiti
    m = re.search(r'(\w+(?:\s+\w+)?)\s+[Mm]ahallesi', tam_metin)
    if m:
        sonuc["mahalle"] = m.group(1) + " Mahallesi"
        parcalar.insert(0, sonuc["mahalle"])

    # 3. Sokak tespiti
    m2 = re.search(r'(\w+(?:\s+\w+)?)\s+[Ss]okak', tam_metin)
    if m2:
        sonuc["sokak"] = m2.group(1) + " Sokak"
        parcalar.insert(0, sonuc["sokak"])

    # 4. Cadde tespiti
    m3 = re.search(r'(\w+(?:\s+\w+)?)\s+[Cc]addesi', tam_metin)
    if m3:
        parcalar.insert(0, m3.group(1) + " Caddesi")

    # 5. Yol referansları
    m4 = re.search(r'(TEM\s*[Oo]toyolu?|D-100|E-5)', tam_metin)
    if m4:
        parcalar.append(m4.group(1))

    if not parcalar:
        # Başlık veya içerikte genel "Kocaeli" geçiyorsa fallback kullan
        if "kocaeli" in baslik_norm or "kocaeli" in icerik_norm[:200]:
            sonuc["ilce"] = "Kocaeli"
            sonuc["metin"] = "Kocaeli"
            enlem, boylam = ILCE_KOORDINATLARI["Kocaeli"]
            sonuc["enlem"] = enlem
            sonuc["boylam"] = boylam
            return sonuc
        return None

    sonuc["metin"] = ", ".join(parcalar) + ", Kocaeli"

    # 6. Geocoding
    koordinatlar = geocode(sonuc["metin"], sonuc["ilce"])
    if not koordinatlar:
        return None

    sonuc["enlem"], sonuc["boylam"] = koordinatlar
    return sonuc


def geocode(adres: str, ilce: str = None) -> tuple | None:
    # Önbellek kontrolü
    cached = cache_col.find_one({"adres": adres})
    if cached:
        return cached["enlem"], cached["boylam"]

    # Google Geocoding API
    if GOOGLE_API_KEY:
        try:
            params = {
                "address": adres + ", Kocaeli, Türkiye",
                "key": GOOGLE_API_KEY,
                "language": "tr",
                "region": "tr",
                "bounds": "40.3,29.0|41.0,30.5"
            }
            r = requests.get(GOOGLE_GEOCODING_URL, params=params, timeout=10)
            r.raise_for_status()
            veri = r.json()

            if veri["status"] == "OK":
                loc = veri["results"][0]["geometry"]["location"]
                enlem = loc["lat"]
                boylam = loc["lng"]
                cache_col.update_one(
                    {"adres": adres},
                    {"$set": {"adres": adres, "enlem": enlem, "boylam": boylam}},
                    upsert=True
                )
                return enlem, boylam
            else:
                print(f"Geocoding başarısız ({veri['status']}): {adres}")
        except Exception as e:
            print(f"Google Geocoding hatası: {e}")

    # Fallback: ilçe koordinatları
    if ilce and ilce in ILCE_KOORDINATLARI:
        enlem, boylam = ILCE_KOORDINATLARI[ilce]
        cache_col.update_one(
            {"adres": adres},
            {"$set": {"adres": adres, "enlem": enlem,
                      "boylam": boylam, "fallback": True}},
            upsert=True
        )
        return enlem, boylam

    return None