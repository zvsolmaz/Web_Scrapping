from datetime import datetime, timedelta
import re

AYLAR = {
    # Tam ad
    "ocak": 1, "subat": 2, "mart": 3, "nisan": 4,
    "mayis": 5, "haziran": 6, "temmuz": 7, "agustos": 8,
    "eylul": 9, "ekim": 10, "kasim": 11, "aralik": 12,
    # Kısaltma (seskocaeli "18 Mar 2026" formatı kullanıyor)
    "oca": 1, "sub": 2, "mar": 3, "nis": 4,
    "may": 5, "haz": 6, "tem": 7, "agu": 8,
    "eyl": 9, "eki": 10, "kas": 11, "ara": 12,
}

def is_within_last_3_days(dt: datetime) -> bool:
    bugun = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    sinir = bugun - timedelta(days=3)
    return dt >= sinir


def parse_turkish_date(tarih_str: str) -> datetime | None:
    if not tarih_str:
        return None

    # Türkçe normalize
    tarih_str = (
        tarih_str.strip()
        .replace("İ", "i").replace("I", "ı")
        .replace("Ğ", "ğ").replace("Ü", "ü")
        .replace("Ş", "ş").replace("Ö", "ö")
        .replace("Ç", "ç")
        .lower()
        .replace("ı", "i").replace("ğ", "g")
        .replace("ü", "u").replace("ş", "s")
        .replace("ö", "o").replace("ç", "c")
    )

    # "15 ocak 2024" veya "15 mar 2026" veya "15 ocak 2024 14:30"
    m = re.search(r'(\d{1,2})\s+([a-z]+)\s+(\d{4})(?:.*?(\d{1,2}):(\d{2}))?', tarih_str)
    if m:
        gun, ay_str, yil, saat, dakika = m.groups()
        ay = AYLAR.get(ay_str[:3])  # ilk 3 harf yeterli
        if ay:
            try:
                return datetime(int(yil), ay, int(gun),
                                int(saat or 0), int(dakika or 0))
            except ValueError:
                pass

    # "2024-01-15" veya "2024-01-15T14:30:00"
    m = re.search(r'(\d{4})-(\d{2})-(\d{2})(?:[T\s](\d{2}):(\d{2}))?', tarih_str)
    if m:
        yil, ay, gun, saat, dakika = m.groups()
        try:
            return datetime(int(yil), int(ay), int(gun),
                            int(saat or 0), int(dakika or 0))
        except ValueError:
            pass

    # "15.01.2024" veya "15.01.2024 14:30"
    m = re.search(r'(\d{2})\.(\d{2})\.(\d{4})(?:\s+(\d{1,2}):(\d{2}))?', tarih_str)
    if m:
        gun, ay, yil, saat, dakika = m.groups()
        try:
            return datetime(int(yil), int(ay), int(gun),
                            int(saat or 0), int(dakika or 0))
        except ValueError:
            pass

    return None