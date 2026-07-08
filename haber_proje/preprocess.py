import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urlunparse  # YENİ EKLENECEK İMPORT


# Reklam / alakasız bölümleri tespit eden kalıplar
REKLAM_KALIPLARI = [
    r"Yorum yazarak.*?sorumlu tutulamaz\.",
    r"Yorumunuz için teşekkürler.*?yayınlanacaktır",
    r"Yorumunuz yarım kaldı.*?tıklayın",
    r"Kırmızı alanlar.*?gönderelim",
    r"Copyright.*?Hakları Saklıdır",
    r"Veri politikasındaki.*?inceleyebilirsiniz\.",
    r"Şimdi oturum açın.*?tıklayın\.",
    r"Haber ajansları tarafından.*?ajanstır\.",
    r"Tüm Hakları Saklıdır.*?Kullanım Şartları",
    r"\d{2,3}\s+\d{3}\s+\d{3}\s+\d{2}\s+\d{2}",
    r"Veri [Pp]olitikası.*?$",
    r"Yazdır\s+Muhabir.*?Merkezi",
    r"çerez konumlandırmaktayız.*",
]


def clean_text(text: str) -> str:
    if not text:
        return ""

    # HTML temizle
    text = BeautifulSoup(text, "html.parser").get_text(" ")

    # Reklam ve alakasız bölümleri temizle
    for kalip in REKLAM_KALIPLARI:
        text = re.sub(kalip, "", text, flags=re.DOTALL | re.UNICODE)

    # Fazla boşlukları temizle
    text = re.sub(r"\s+", " ", text)

    # Gereksiz karakterleri temizle (Türkçe karakterler korunur)
    text = re.sub(r"[^\w\sçğıöşüÇĞİÖŞÜ.,:;!?'\-]", " ", text, flags=re.UNICODE)

    return text.strip()


def normalize_text(text: str) -> str:
    """
    Türkçe karakterleri doğru küçültür.
    Python'un .lower() metodu İ → i̇ (iki karakter) yapıyor, bu yanlış.
    """
    text = clean_text(text)

    text = (
        text
        .replace("İ", "i")
        .replace("I", "ı")
        .replace("Ğ", "ğ")
        .replace("Ü", "ü")
        .replace("Ş", "ş")
        .replace("Ö", "ö")
        .replace("Ç", "ç")
    )

    return text.lower()

# --- YENİ EKLENEN FONKSİYON ---
def clean_url(url):
    """
    Linkin sonundaki ?ref=... veya #section gibi gereksiz parametreleri temizler.
    Böylece 'haber.html' ve 'haber.html?ref=anasayfa' aynı kabul edilir.
    """
    try:
        parsed = urlparse(url)
        # scheme, netloc, path, params, query, fragment
        # query (4. parametre) ve fragment (5. parametre) siliniyor
        return urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', '', ''))
    except:
        return url