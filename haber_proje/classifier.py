from preprocess import normalize_text

# --- LİSTELER ---

SPOR_ENGEL = [
    "kocaelispor", "fenerbahce", "galatasaray", "besiktas", "trabzonspor",
    "futbol turnuvasi", "teknik direktor", "taraftar", "stadyum", "penalti",
    "sampiyonluk", "basketbol ligi", "voleybol ligi",
    "milli takim mac", "deplasman", "tribun","karate", "judo", "gures", "boks","tenis", "masa tenisi", "okculuk", "taekwondo",
    "play-off", "playoff", "lig mac", "mac skoru",
    "puan tablosu", "gol atti", "kupa mac", "spor toto", "geleneksel okcu", "geleneksel okcular",
    "u-14", "u-15", "u-16", "u-17", "u-18", "u-13",
    "gebzespor", "korfez genclerbirligi", "darica birlik", "karamursel idman",
    "5-0", "4-0", "3-0", "2-0", "1-0", "0-1", "0-2", "0-3",
    "maglup", "galibiyet", "beraberlik", "puan aldi",
]

# Asayiş haberlerini engellemek için kara liste
ASAYIS_ENGEL = [
    "darp", "yaralama", "kavga", "saldiri", "bicaklama",
    "tecavuz", "cinsel istismar", "cinayet",
    "siddet", "tehdit", "bosanma", "olduresiye", "dayak",
    "dovdu", "dovuldu", "oldur", "cetesi", "cete", "deprem",
    "uyusturucu","silahli saldiri",
]

# Yanlış pozitif (false positive) haberleri engelleyen liste
# Bunlar gerçek kategori kelimesi içerse de konu dışıdır.
KATEGORI_DISI_ENGEL = [
    "ihale", "ihaleye", "ihalesi",                        # İhale haberleri
    "otv siz", "otvsiz", "otv muaf",                      # ÖTV haberleri
    "agir tonajli arac", "arac giremeyecek",              # Trafik yasağı (kaza değil)
    "balik fiyat", "balik cesitlilik",                    # Piyasa fiyatları
    "sunnet toreni",                            # Sünnet töreni
    "hukuk balosu",                                       # Balo
    "nobet gecirdi",                                      # Hastalık nöbeti
    "dogum gunu kutla",                                   # Doğum günü
    "kurbanlık pazarlik", "kurban fiyat",                 # Kurban fiyatları
    "kongre yapildi", "baskani secildi", "baskan secildi",
    "siyasete adim",# Kongre seçimi
    
]

CATEGORY_KEYWORDS = {
    "Yangın": [
        "yangin", "yangini", "yanginda", "yangininda", "yangin cikti",
        "alev aldi", "alevler sardi", "alevler", "itfaiye",
        "duman", "ev yandi", "bina yandi", "fabrika yandi", "araç yandi",
        "orman yandi", "is yeri yandi", "ahir yandi", "yaniyor", "tutustu", "yanginina", "yangina",
        "kul oldu", "sondurme", "yangin ekibi", "alevlere teslim",
        "kundaklama", "kundaklamasi",
        "patlama", "dogal gaz patla", 
    ],
    "Elektrik Kesintisi": [
        "elektrik kesintisi", "planli kesinti", "elektrik verilemeyecek",
        "sepas", "enerji kesintisi", "elektrik kesildi", "elektrik yok",
        "trafo arizasi", "hat arizasi", "elektrik arizasi",
        "ilce elektriksiz", "elektriksiz kalacak",
        "elektrik kesintileri", "sedas", "jenerator",
        "elektriksiz", "elektrik ariza",
    ],
    "Hırsızlık": [
        "hirsizlik", "hirsiz", "calindi", "caldi", "caldilar",
        "soygun", "soyuldu", "soydu", "calinan",
        "hirsizlar yakalandilar", "hirsiz yakalandi",
        "gasp", "kapcak", "yankesicilik", "arac calindi",
        "evden hirsizlik", "kumar baskini", "rusvet operasyonu",
        "dolandiricilik", "dolandirdi", "dolandirildi",
        "kasayi caldi", "telefon calindi",
        "motosiklet calindi", "bisiklet calindi",
    ],
    "Trafik Kazası": [
        "trafik kazasi", "zincirleme kaza", "trafik kazasinda",
        "feci kaza", "feci kazada", "kaza ani", "can pazarinda","kazada hayatini kaybetti","kazada oldu","kazada can verdi","tem de kaza","otoyolda kaza",
        "carpisti", "carpisma", "motosiklet kazasi","kazayi getirdi", "kazaya neden oldu", "kazaya yol acti",
        "tem de kaza", "d-100 de kaza", "otoyolda kaza","olumlu kaza","kazada yaşamini","kazada hayatini",
        "kaza yapti", "arac devrildi", "takla atti","bariyere carpti", "bariyerlere carpti",
        "yarali kaldirildi","kontrolden cikti", "kontrolden cikan arac","korkutan kaza", "otomobil daldi", "araca daldi","birbirine katti", "arac binaya", "arac duvara",
        "tira carpan", "otomobil devrildi", "birbirine girdi",
        "kazada yaralandi", "kaza sonucu", "kavsakta kaza",
        "otomobil carpti", "kamyon carpti", "otobus kazasi",
        "servis araci kazasi",
    ],
    "Kültürel Etkinlikler": [
        "konser", "festival", "senlik", "tiyatro",
        "sergi", "fuar", "resital", "muze",
        "kultur merkezi etkinlik", "sanat etkinligi", "egitim programi","piyano resitali",
        "jolly joker", "sdkm", "hayal kahvesi",  "sanat atolye", "sanat egitim", "hayat okulu", 
        "iftar programi", "kadir gecesi", "kandil programi", "mevlid programi",
        "sokak iftari", "lunapark",
        "acilis toreni", "anma programi", "canakkale anma", "canakkale zaferi",
        "kermes", "bayramlasma toreni", "kulturel etkinlik",
        "bayrami kutlaniyor", "bayram etkinlik",
    ],
}

CATEGORY_PRIORITY = [
    "Yangın",
    "Elektrik Kesintisi",
    "Hırsızlık",
    "Trafik Kazası",
    "Kültürel Etkinlikler",
]

# --- FONKSİYONLAR ---

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

def classify_news(title: str, content: str = "") -> str | None:
    title_norm = turkce_norm(title)

    # 1. Spor engeli
    if any(engel in title_norm for engel in SPOR_ENGEL):
        return None

    # 2. Kategori dışı engeli (ihale, ÖTV, fiyat haberleri vb.)
    if any(engel in title_norm for engel in KATEGORI_DISI_ENGEL):
        return None

    # 3. Kategori ara (öncelik sırasına göre)
    bulunan = None
    for category in CATEGORY_PRIORITY:
        if any(kw in title_norm for kw in CATEGORY_KEYWORDS[category]):
            bulunan = category
            break

    # 4. Kategori bulunduysa döndür
    if bulunan:
        return bulunan

    # 5. Başlıkta bulunamadıysa asayiş engeli kontrol et
    if any(engel in title_norm for engel in ASAYIS_ENGEL):
        return None

    # 6. İçerikte ara (ilk 200 karakter)
    if content:
        content_norm = turkce_norm(content[:300])
        if any(engel in content_norm for engel in SPOR_ENGEL):
            return None
        if any(engel in content_norm for engel in KATEGORI_DISI_ENGEL):
            return None
        for category in CATEGORY_PRIORITY:
            if any(kw in content_norm for kw in CATEGORY_KEYWORDS[category]):
                return category

    return None
