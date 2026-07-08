@echo off
echo ============================================
echo  Kocaeli Haber Haritasi - Kurulum (Windows)
echo ============================================

:: Python kontrolu
python --version >nul 2>&1
if errorlevel 1 (
    echo [HATA] Python bulunamadi! https://www.python.org adresinden yukleyin.
    pause
    exit /b 1
)

:: Sanal ortam oluştur
echo.
echo [1/4] Sanal ortam olusturuluyor...
python -m venv venv
if errorlevel 1 (
    echo [HATA] Sanal ortam olusturulamadi.
    pause
    exit /b 1
)

:: Sanal ortamı aktive et
echo [2/4] Sanal ortam aktive ediliyor...
call venv\Scripts\activate.bat

:: pip'i güncelle
echo [3/4] pip guncelleniyor...
python -m pip install --upgrade pip --quiet

:: Kütüphaneleri kur
echo [4/4] Kutuphaneler kuruluyor (bu 3-5 dakika surebilir)...
pip install -r requirements.txt
if errorlevel 1 (
    echo [HATA] Kutuphane kurulumu basarisiz.
    pause
    exit /b 1
)

:: .env dosyası yoksa örnek oluştur
if not exist .env (
    echo.
    echo [BILGI] .env dosyasi olusturuluyor...
    (
        echo MONGO_URI=mongodb://localhost:27017/
        echo GOOGLE_MAPS_API_KEY=BURAYA_API_KEYINIZI_YAZIN
    ) > .env
    echo [UYARI] .env dosyasini acip API keyinizi girin!
)

echo.
echo ============================================
echo  Kurulum tamamlandi!
echo.
echo  Calistirmak icin:
echo    venv\Scripts\activate
echo    uvicorn main:app --reload --port 8000
echo ============================================
pause
