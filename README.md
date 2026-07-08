# Web_Scrapping
# Web Scraping Tabanlı Kentsel Haber İzleme ve Harita Üzerinde Görselleştirme Sistemi

Bu proje, Kocaeli iline ait yerel haber sitelerinden otomatik olarak veri toplayan, toplanan haberleri doğal dil işleme teknikleriyle sınıflandıran, coğrafi konum bilgisini çıkarıp Google Maps üzerinde interaktif olarak görselleştiren uçtan uca (end-to-end) bir sistemdir.

## 📊 Ekran Görüntüleri

### Genel Bakış ve Filtreleme Paneli
![Kocaeli Haber Haritası Genel Görünüm](images/Ekran%20görüntüsü%202026-07-08%20205723.png)

### Sol Panel (Son Haberler Listesi)
![Son Haberler Listesi](images/Ekran%20görüntüsü%202026-07-08%20205733.png)

### Harita İşaretçi Detayı (Mükerrer Haber Birleştirme)
![Marker Detay Penceresi](images/Ekran%20görüntüsü%202026-07-08%20205741.png)

## 🚀 Özellikler

* **Çoklu Kaynaktan Web Scraping:** Kocaeli'nin önde gelen 5 yerel haber sitesinden (`cagdaskocaeli.com.tr`, `ozgurkocaeli.com.tr`, `seskocaeli.com`, `yenikocaeli.com` ve `bizimyaka.com`) son 3 güne ait veriler anlık olarak çekilir.
* **SSL Hata Toleransı:** `safe_get()` fonksiyonu sayesinde SSLv3 handshake hatası veren sitelerden bile kesintisiz veri toplanır.
* **NLP Tabanlı Duplicate (Mükerrer) Tespiti:** Üç kademeli kontrol (Link, Başlık ve `paraphrase-multilingual-MiniLM-L12-v2` embedding modeli ile %90 üzeri Cosine benzerliği) sayesinde farklı sitelerdeki aynı haberler tek bir harita marker'ı altında birleştirilir.
* **Akıllı Haber Sınıflandırma:** Haberler öncelik sırasına göre (Yangın, Elektrik Kesintisi, Hırsızlık, Trafik Kazası, Kültürel Etkinlikler) anahtar kelime tabanlı ve Türkçe karakter normalizasyonlu olarak sınıflandırılır.
* **Gelişmiş Konum Çıkarımı:** "En erken pozisyon yöntemi" kullanılarak ajans imzaları elenir. Regex ile Mahalle, Sokak ve Cadde tespiti yapılarak Google Geocoding API ile koordinatlara dönüştürülür.
* **Performans & Önbellekleme:** Mükerrer Google API çağrılarını önlemek amacıyla coğrafi kodlama sonuçları MongoDB'de `konum_cache` koleksiyonunda önbelleğe alınır.
* **Dinamik Filtreleme Paneli:** Kullanıcı arayüzü üzerinden harita yenilenmeden ilçe, haber türü ve tarih bazında dinamik filtreleme yapılabilir.

## 🛠️ Sistem Mimarisi

Sistem 4 ana katmandan oluşmaktadır:
1. **Web Scraping Katmanı:** BeautifulSoup tabanlı Python modülü.
2. **Sınıflandırma ve Ön İşleme Katmanı:** Metin temizleme, normalizasyon ve kategori belirleme motoru.
3. **Konum ve Geocoding Katmanı:** Adres çıkarımı, koordinat dönüşümü ve MongoDB cache mekanizması.
4. **API ve Görselleştirme Katmanı:** FastAPI RESTful backend ve Google Maps JavaScript API entegrasyonlu ön yüz.

## 📋 Gereksinimler ve Kurulum

### Ön Gereksinimler
* Python 3.9+
* MongoDB
* Google Maps & Geocoding API Anahtarı (Key)

### Kurulum Adımları

1. Projeyi klonlayın:
``bash
git clone [https://github.com/kullaniciadi/kentsel-haber-izleme.git](https://github.com/kullaniciadi/kentsel-haber-izleme.git)
cd kentsel-haber-izleme
Gerekli kütüphaneleri yükleyin:Bashpip install -r requirements.txt
Kök dizinde bir .env dosyası oluşturun ve API anahtarlarınızı tanımlayın:  
Kod snippet'iMONGO_URI=mongodb://localhost:27017/
GOOGLE_API_KEY=YOUR_GOOGLE_MAPS_API_KEY
Backend servisini (FastAPI) başlatın:Bashuvicorn main:app --reload


---

# Web Scraping Based Urban News Monitoring and Map Visualization System [cite: 1]

This project is an end-to-end system developed to automatically collect data from local news websites in Kocaeli, classify them using natural language processing (NLP) techniques, extract geographical location information, and visualize them interactively on Google Maps[cite: 6].

## 🚀 Features

* **Multi-Source Web Scraping:** Real-time data scraping from 5 local news sources (`cagdaskocaeli.com.tr`, `ozgurkocaeli.com.tr`, `seskocaeli.com`, `yenikocaeli.com`, and `bizimyaka.com`) capturing news from the last 3 days[cite: 26, 27].
* **SSL Fault Tolerance:** Continuous data extraction even from sites with SSLv3 handshake errors using a custom `safe_get()` mechanism[cite: 29, 30].
* **NLP-Based Deduplication:** A 3-tier duplicate check (Link, Title, and Embedding-based similarity using `paraphrase-multilingual-MiniLM-L12-v2` with 90% or higher Cosine similarity) merges identical news from different sources under a single map marker[cite: 39, 40, 41, 42, 43, 44].
* **Smart News Classification:** Keyword-based classification with Turkish character normalization based on a strict priority queue: (1) Fire, (2) Power Outage, (3) Theft, (4) Traffic Accident, (5) Cultural Events[cite: 49, 53, 54].
* **Advanced Location Extraction:** Employs the "earliest position method" to prevent false positives from agency signatures[cite: 67, 68, 69]. It uses Regex to capture Neighborhood, Street, and Avenue entities, converting them to coordinates via Google Geocoding API[cite: 71, 72, 81].
* **Performance & Caching:** Geocoding results are cached in MongoDB's `konum_cache` collection to eliminate redundant and costly Google API calls[cite: 82, 127].
* **Dynamic Filtering Panel:** Offers a user-friendly UI sidebar to filter incidents by district, news type, and date range dynamically without reloading the map[cite: 90, 95, 96].

## 🛠️ System Architecture

The framework consists of 4 main layers[cite: 18]:
1. **Web Scraping Layer:** BeautifulSoup-based Python scraping module[cite: 15, 19].
2. **Classification & Preprocessing Layer:** Text cleaning, normalization, and category matching engine[cite: 15, 20].
3. **Location & Geocoding Layer:** Address extraction, coordinate transformation, and MongoDB caching[cite: 21, 82].
4. **API & Visualization Layer:** FastAPI RESTful backend paired with a Google Maps JavaScript API frontend[cite: 15, 16, 22].

## 📋 Requirements & Installation

### Prerequisites
* Python 3.9+
* MongoDB [cite: 5, 127]
* Google Maps & Geocoding API Key [cite: 15, 81]

### Setup Instructions

1. Clone the repository:
   ```bash
   git clone [https://github.com/username/urban-news-monitoring.git](https://github.com/username/urban-news-monitoring.git)
   cd urban-news-monitoring
Install the dependencies:Bashpip install -r requirements.txt
Create a .env file in the root directory and add your API keys:  Kod snippet'iMONGO_URI=mongodb://localhost:27017/
GOOGLE_API_KEY=YOUR_GOOGLE_MAPS_API_KEY
Run the FastAPI backend server:Bashuvicorn main:app --reload
