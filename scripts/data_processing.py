import pandas as pd
import json
from math import sqrt
import os

# Dosya yollarını düzgün şekilde oluştur
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))

# İl sınırlarını yükle
json_path = os.path.join(project_root, 'YapayZekaSon1', 'data', 'turkiye_il_koordinatlari.json')
with open(json_path, 'r', encoding='utf-8') as f:
    il_sinirlar = json.load(f)

def mesafe_hesapla(lat1, lon1, lat2, lon2):
    """
    İki koordinat arasındaki yaklaşık mesafeyi hesaplar
    """
    return sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2)

def koordinat_ile_sehir_bul(lat, lon):
    """
    Verilen koordinatların hangi ile ait olduğunu bulur
    En yakın il merkezi ve sınır kontrolü ile belirlenir
    """
    olasi_iller = []
    
    for il, sinirlar in il_sinirlar.items():
        if (sinirlar['lat_min'] - 1.4 <= lat <= sinirlar['lat_max'] + 1.4 and 
            sinirlar['lon_min'] - 1.4 <= lon <= sinirlar['lon_max'] + 1.4):
            merkez_lat = (sinirlar['lat_min'] + sinirlar['lat_max']) / 2
            merkez_lon = (sinirlar['lon_min'] + sinirlar['lon_max']) / 2
            mesafe = mesafe_hesapla(lat, lon, merkez_lat, merkez_lon)
            olasi_iller.append((il, mesafe))
    
    if not olasi_iller:
        return 'BELIRSIZ'
    
    en_yakin_il = min(olasi_iller, key=lambda x: x[1])
    return en_yakin_il[0]

# Veriyi işle
input_csv_path = os.path.join(project_root, 'YapayZekaSon1', 'data', 'earthquakes.csv')
df = pd.read_csv(input_csv_path)
df['Il'] = df.apply(lambda row: koordinat_ile_sehir_bul(row['Enlem'], row['Boylam']), axis=1)

# Tarih sütununu datetime formatına çevir
df['Tarih_Saat'] = pd.to_datetime(df['Tarih'])

# Yeni DataFrame oluştur
new_df = pd.DataFrame()
new_df['Tarih_Saat'] = df['Tarih_Saat']
new_df['Konum'] = df['Il']
new_df['Buyukluk'] = df['Buyukluk']

# Sonuçları kaydet
output_csv_path = os.path.join(project_root, 'YapayZekaSon1', 'data', 'updated_earthquakes.csv')
os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)

# Eğer dosya zaten varsa, mevcut veri sayısını al
existing_count = 0
if os.path.exists(output_csv_path):
    existing_df = pd.read_csv(output_csv_path)
    existing_count = len(existing_df)

# Yeni verileri kaydet
new_df.to_csv(output_csv_path, index=False, encoding='utf-8')

# Yeni ve eski veri sayılarını karşılaştır
new_count = len(new_df)
if existing_count > 0:
    added_records = new_count - existing_count
    print(f"İşlem tamamlandı:")
    print(f"Önceki veri sayısı: {existing_count}")
    print(f"Yeni veri sayısı: {new_count}")
    print(f"Eklenen yeni veri sayısı: {added_records}")
else:
    print(f"İşlem tamamlandı. Toplam {new_count} veri eklendi.")
