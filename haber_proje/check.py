from pymongo import MongoClient
db = MongoClient()['haber_db']

toplam = db.haberler.count_documents({})
tarihli = db.haberler.count_documents({"published_at": {"$ne": None}})
print(f"Toplam: {toplam}")
print(f"Tarih var: {tarihli}")
print(f"Tarih yok: {toplam - tarihli}")