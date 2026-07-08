"""
Kocaeli Haber Haritası - FastAPI Backend
"""

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime, timedelta
from typing import Optional
import os
import subprocess
import threading
import sys

load_dotenv()

app = FastAPI(title="Kocaeli Haber Haritası API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["haber_db"]


# ─── STATIC FILES ───
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def index():
    return FileResponse("static/index.html")


# ─── HABERLER ───
@app.get("/api/haberler")
def haberleri_getir(
    haber_turu: Optional[str] = Query(None),
    ilce: Optional[str] = Query(None),
    baslangic: Optional[str] = Query(None),
    bitis: Optional[str] = Query(None),
):
    filtre = {
        "konum": {"$ne": None},
        "konum.enlem": {"$exists": True, "$ne": None},
    }

    if haber_turu:
        filtre["haber_turu"] = haber_turu

    if ilce:
        filtre["konum.ilce"] = ilce

    tarih_filtre = {}
    if baslangic:
        try:
            tarih_filtre["$gte"] = datetime.fromisoformat(baslangic)
        except:
            pass
    if bitis:
        try:
            tarih_filtre["$lte"] = datetime.fromisoformat(bitis) + timedelta(days=1)
        except:
            pass
    if tarih_filtre:
        filtre["published_at"] = tarih_filtre

    haberler = []
    for h in db.haberler.find(filtre, {"embedding": 0}).sort("published_at", -1).limit(500):
        h["_id"] = str(h["_id"])
        if h.get("published_at"):
            h["published_at"] = h["published_at"].isoformat()
        haberler.append(h)

    return {"haberler": haberler, "toplam": len(haberler)}


# ─── İLÇELER ───
@app.get("/api/ilceler")
def ilceleri_getir():
    return {
        "ilceler": [
            "Başiskele", "Çayırova", "Darıca", "Derince", "Dilovası",
            "Gebze", "Gölcük", "Kandıra", "Karamürsel", "Kartepe",
            "Körfez", "İzmit"
        ]
    }


# ─── KATEGORİLER ───
@app.get("/api/kategoriler")
def kategorileri_getir():
    return {
        "kategoriler": [
            "Trafik Kazası",
            "Yangın",
            "Elektrik Kesintisi",
            "Hırsızlık",
            "Kültürel Etkinlikler"
        ]
    }


# ─── SCRAPING TETİKLE ───
scraping_durumu = {"calisıyor": False, "son_calisma": None, "sonuc": None}

def scraping_calistir():
    try:
        result = subprocess.run(
            [sys.executable, "scraper_runner.py"],
            capture_output=True, text=True, timeout=1200,
            encoding="utf-8",
            env={**os.environ, "PYTHONIOENCODING": "utf-8"}
        )
        if result.returncode == 0:
            scraping_durumu["sonuc"] = "tamamlandi"
        else:
            scraping_durumu["sonuc"] = f"hata: {result.stderr[-500:]}"
    except Exception as e:
        scraping_durumu["sonuc"] = f"hata: {e}"
    finally:
        scraping_durumu["calisıyor"] = False
        scraping_durumu["son_calisma"] = datetime.now().isoformat()

@app.post("/api/scrape")
def scraping_baslat():
    if scraping_durumu["calisıyor"]:
        return {"mesaj": "Scraping zaten çalışıyor", "durum": "calisıyor"}
    # Durumu sıfırla ve hemen calisıyor yap
    scraping_durumu["sonuc"] = None
    scraping_durumu["calisıyor"] = True
    t = threading.Thread(target=scraping_calistir)
    t.daemon = True
    t.start()
    return {"mesaj": "Scraping başlatıldı", "durum": "baslatildi"}

@app.get("/api/scrape/durum")
def scraping_durumu_getir():
    return scraping_durumu


# ─── İSTATİSTİK ───
@app.get("/api/istatistik")
def istatistik():
    from collections import Counter
    haberler = list(db.haberler.find({}, {"haber_turu": 1, "source": 1}))
    tur_dagilim = Counter(h["haber_turu"] for h in haberler)
    kaynak_dagilim = Counter(h["source"] for h in haberler)
    return {
        "toplam": len(haberler),
        "tur_dagilim": dict(tur_dagilim),
        "kaynak_dagilim": dict(kaynak_dagilim)
    }