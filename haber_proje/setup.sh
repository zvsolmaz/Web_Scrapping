#!/bin/bash
echo "============================================"
echo " Kocaeli Haber Haritasi - Kurulum (Linux/Mac)"
echo "============================================"

# Python kontrolü
if ! command -v python3 &> /dev/null; then
    echo "[HATA] Python3 bulunamadi! Lutfen yukleyin."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "Python versiyonu: $PYTHON_VERSION"

# Sanal ortam oluştur
echo ""
echo "[1/4] Sanal ortam olusturuluyor..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "[HATA] Sanal ortam olusturulamadi."
    exit 1
fi

# Aktive et
echo "[2/4] Sanal ortam aktive ediliyor..."
source venv/bin/activate

# pip güncelle
echo "[3/4] pip guncelleniyor..."
pip install --upgrade pip --quiet

# Kütüphaneler
echo "[4/4] Kutuphaneler kuruluyor (bu 3-5 dakika surebilir)..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "[HATA] Kutuphane kurulumu basarisiz."
    exit 1
fi

# .env dosyası
if [ ! -f .env ]; then
    echo ""
    echo "[BILGI] .env dosyasi olusturuluyor..."
    cat > .env << 'ENVEOF'
MONGO_URI=mongodb://localhost:27017/
GOOGLE_MAPS_API_KEY=BURAYA_API_KEYINIZI_YAZIN
ENVEOF
    echo "[UYARI] .env dosyasini acip GOOGLE_MAPS_API_KEY degerini girin!"
fi

echo ""
echo "============================================"
echo " Kurulum tamamlandi!"
echo ""
echo " Calistirmak icin:"
echo "   source venv/bin/activate"
echo "   uvicorn main:app --reload --port 8000"
echo "============================================"
