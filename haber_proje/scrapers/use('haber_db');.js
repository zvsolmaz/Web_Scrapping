use('haber_db');
db.haberler.find(
  { ilce: "Kandira" },
  { title: 1, ilce: 1, "konum.ilce": 1, konum: 1, _id: 0 }
).limit(3);