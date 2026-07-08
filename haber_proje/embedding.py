"""
Embedding Tabanlı Duplicate Tespiti
- sentence-transformers: paraphrase-multilingual-MiniLM-L12-v2
- Başlık 3x + içerik ilk 300 karakter
- Cosine benzerliği %90+ ise aynı haber kabul edilir
"""

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from pymongo import MongoClient
from dotenv import load_dotenv
import numpy as np
import os

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
BENZERLIK_ESIGI = 0.90

print("Embedding modeli yükleniyor...")
MODEL = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
print("Model hazır.")


def metin_hazirla(baslik: str, icerik: str = "") -> str:
    """Başlık 3x + içerik ilk 300 karakter."""
    return " ".join([baslik] * 3) + " " + icerik[:300]


def embedding_hesapla(metin: str) -> list:
    vektor = MODEL.encode(metin, normalize_embeddings=True)
    return vektor.tolist()


def cosine_hesapla(v1: list, v2: list) -> float:
    a = np.array(v1).reshape(1, -1)
    b = np.array(v2).reshape(1, -1)
    return float(cosine_similarity(a, b)[0][0])


def duplicate_bul(baslik: str, icerik: str = "") -> dict | None:
    """
    Yeni haberi mevcut haberlerle karşılaştırır.
    %90+ benzerlik varsa duplicate kabul edilir.
    """
    yeni_metin = metin_hazirla(baslik, icerik)
    yeni_embedding = embedding_hesapla(yeni_metin)

    client = MongoClient(MONGO_URI)
    collection = client["haber_db"]["haberler"]

    en_yuksek_skor = 0
    en_benzer = None

    for haber in collection.find(
        {"embedding": {"$exists": True}},
        {"title": 1, "content_raw": 1, "embedding": 1, "kaynaklar": 1}
    ):
        mevcut_emb = haber.get("embedding")
        if not mevcut_emb:
            continue
        skor = cosine_hesapla(yeni_embedding, mevcut_emb)
        if skor > en_yuksek_skor:
            en_yuksek_skor = skor
            en_benzer = haber

    client.close()

    if en_yuksek_skor >= BENZERLIK_ESIGI:
        print(f"  🔁 Duplicate (skor={en_yuksek_skor:.2f}): {en_benzer.get('title', '')[:50]}")
        return en_benzer

    return None


def kaynak_ekle(mevcut_id, yeni_kaynak: dict):
    client = MongoClient(MONGO_URI)
    collection = client["haber_db"]["haberler"]
    collection.update_one(
        {"_id": mevcut_id},
        {"$addToSet": {"kaynaklar": yeni_kaynak}}
    )
    client.close()
    print(f"  📎 Yeni kaynak eklendi: {yeni_kaynak['site_adi']}")