"""
SSL sertifika doğrulaması sorunlu olan siteler için
güvenli HTTP session oluşturur.

seskocaeli.com, bizimyaka.com ve yenikocaeli.com gibi siteler
SSLv3 handshake hatası veriyor. Bu modül:
  1. Önce normal HTTPS bağlantısı dener.
  2. SSL hatası alınırsa verify=False ile tekrar dener.
  3. Her iki durumda da makul zaman aşımı uygular.
"""

import requests
import urllib3
import logging

# SSL uyarılarını bastır (verify=False durumunda terminali kirletmesin)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8",
}


def make_session(headers: dict = None) -> requests.Session:
    """Standart bir requests session döndürür."""
    session = requests.Session()
    session.headers.update(headers or DEFAULT_HEADERS)
    return session


def safe_get(url: str, session: requests.Session = None, timeout: int = 30) -> requests.Response:
    """
    Verilen URL'yi çeker. SSL hatası alınırsa verify=False ile tekrar dener.
    İstisna fırlatmak yerine None döndürür — çağıran kod hatayı loglamalıdır.
    """
    if session is None:
        session = make_session()

    # 1. Deneme: normal SSL doğrulaması
    try:
        response = session.get(url, timeout=timeout, verify=True)
        response.raise_for_status()
        return response
    except requests.exceptions.SSLError:
        pass  # SSL hatası → 2. denemeye geç
    except requests.exceptions.Timeout:
        pass  # Timeout → 2. denemeye geç
    except Exception as e:
        logging.warning(f"[safe_get] Normal istek başarısız ({url}): {e}")
        return None

    # 2. Deneme: SSL doğrulaması kapalı, daha uzun timeout
    try:
        response = session.get(url, timeout=timeout + 15, verify=False)
        response.raise_for_status()
        return response
    except Exception as e:
        logging.warning(f"[safe_get] SSL-off istek de başarısız ({url}): {e}")
        return None
