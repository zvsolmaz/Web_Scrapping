from scrapers.cagdas import fetch_cagdas_news
from scrapers.ozgur import fetch_ozgur_news
from scrapers.ses import fetch_ses_news
from scrapers.bizimyaka import fetch_bizimyaka_news
from scrapers.yeni import fetch_yeni_news
from utils.db import haberler_collection
from location_extractor import konum_cikar
from embedding import embedding_hesapla, metin_hazirla, duplicate_bul, kaynak_ekle


def save_news_items(news_items):
    eklenen = 0
    atlanan = 0
    duplicate = 0

    # Bu çağrı içinde işlenen başlıkları takip et (aynı batch içi tekrar)
    islenen_basliklar = set()
    islenen_linkler = set()

    for item in news_items:
        if not item.get("haber_turu"):
            continue

        link = item["link"]
        baslik = item["title"]

        # 1. Bu batch içinde aynı link var mı?
        if link in islenen_linkler:
            atlanan += 1
            continue
        islenen_linkler.add(link)

        # 2. DB'de link duplicate kontrolü
        if haberler_collection.find_one({"link": link}):
            atlanan += 1
            continue

        # 3. Bu batch içinde aynı başlık var mı?
        if baslik in islenen_basliklar:
            duplicate += 1
            continue
        islenen_basliklar.add(baslik)

        # 4. DB'de başlık duplicate kontrolü
        mevcut_baslik = haberler_collection.find_one({"title": baslik})
        if mevcut_baslik:
            kaynak_ekle(mevcut_baslik["_id"], {
                "site_adi": item["source"],
                "link": link
            })
            print(f"  🔁 Başlık dup: {baslik[:55]}")
            duplicate += 1
            continue

        # 5. Embedding bazlı duplicate kontrolü (%90+)
        mevcut = duplicate_bul(baslik, item.get("content_raw", ""))
        if mevcut:
            kaynak_ekle(mevcut["_id"], {
                "site_adi": item["source"],
                "link": link
            })
            duplicate += 1
            continue

        # 6. Konum çıkarımı
        konum = konum_cikar(baslik, item.get("content_raw", ""))
        if konum:
            item["konum"] = konum
            item["raw_location_text"] = konum["metin"]
        else:
            item["konum"] = None
            item["raw_location_text"] = None

        # 7. Kaynaklar listesi
        item["kaynaklar"] = [{"site_adi": item["source"], "link": link}]

        # 8. Embedding hesapla ve kaydet
        metin = metin_hazirla(baslik, item.get("content_raw", ""))
        item["embedding"] = embedding_hesapla(metin)

        # 9. MongoDB'ye kaydet
        haberler_collection.insert_one(item)
        konum_str = konum["ilce"] if konum else "konum yok"
        print(f"✅ [{item['haber_turu']}] [{konum_str}] {baslik[:55]}")
        eklenen += 1

    return eklenen, atlanan, duplicate


def main():
    siteler = [
        ("cagdaskocaeli", fetch_cagdas_news),
        ("ozgurkocaeli",  fetch_ozgur_news),
        ("seskocaeli",    fetch_ses_news),
        ("bizimyaka",     fetch_bizimyaka_news),
        ("yenikocaeli",   fetch_yeni_news),
    ]

    toplam_eklenen = 0
    toplam_atlanan = 0
    toplam_duplicate = 0

    for site_adi, fetch_fn in siteler:
        print(f"\n{'='*50}")
        print(f"🔄 {site_adi} çekiliyor...")
        print(f"{'='*50}")

        try:
            haberler = fetch_fn()
            eklenen, atlanan, duplicate = save_news_items(haberler)
            toplam_eklenen += eklenen
            toplam_atlanan += atlanan
            toplam_duplicate += duplicate
            print(f"📊 {site_adi}: {eklenen} eklendi, {atlanan} link dup, {duplicate} içerik dup")
        except Exception as e:
            print(f"❌ {site_adi} hatası: {e}")

    print(f"\n{'='*50}")
    print(f"🏁 TOPLAM: {toplam_eklenen} eklendi | {toplam_atlanan} link dup | {toplam_duplicate} içerik dup")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()