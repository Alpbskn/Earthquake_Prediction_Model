import requests
import pandas as pd
from datetime import datetime, timedelta
import os

def get_kandilli_data():
    # Kandilli Rasathanesi API URL'i
    url = "http://www.koeri.boun.edu.tr/scripts/lst0.asp"
    
    try:
        # Verileri çek
        response = requests.get(url)
        response.encoding = 'utf-8'  # Türkçe karakterler için encoding ayarı
        
        # Ham veriyi satırlara böl
        lines = response.text.split("\n")
        
        # Veri başlangıç indeksini bul (veriler genelde 6. satırdan başlar)
        start_index = 6
        data = []
        
        # Her bir satırı işle
        for line in lines[start_index:]:
            if line.strip() and len(line) > 120:  # Boş olmayan ve yeterli uzunlukta satırları al
                try:
                    # Satırı parçalara ayır
                    parts = line.split()
                    
                    # Tarih ve saat bilgisini birleştir
                    date_str = f"{parts[0]} {parts[1]}"
                    date = datetime.strptime(date_str, "%Y.%m.%d %H:%M:%S")
                    
                    # Veri sözlüğü oluştur
                    earthquake = {
                        'Tarih': date,
                        'Enlem': float(parts[2]),
                        'Boylam': float(parts[3]),
                        'Derinlik': float(parts[4]),
                        'Buyukluk': float(parts[6]),
                        'Yer': ' '.join(parts[8:]).strip()
                    }
                    
                    data.append(earthquake)
                except:
                    continue
        
        # Yeni verileri DataFrame'e dönüştür
        new_df = pd.DataFrame(data)
        
        # CSV dosyası varsa oku, yoksa boş DataFrame oluştur
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        csv_path = os.path.join(project_root, 'YapayZekaSon1', 'data', 'earthquakes.csv')
        
        # Dizinin var olduğundan emin ol
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)
        
        try:
            if os.path.exists(csv_path):
                existing_df = pd.read_csv(csv_path)
                # Tarih sütununu datetime formatına çevir
                existing_df['Tarih'] = pd.to_datetime(existing_df['Tarih'])
                new_df['Tarih'] = pd.to_datetime(new_df['Tarih'])
                
                # Mevcut ve yeni verileri birleştir
                combined_df = pd.concat([new_df, existing_df], ignore_index=True)
                
                # Tekrarlanan kayıtları kaldır (Tarih, Enlem, Boylam'a göre)
                combined_df = combined_df.drop_duplicates(subset=['Tarih', 'Enlem', 'Boylam'], keep='first')
                
                # Tarihe göre sırala (en yeni en üstte)
                combined_df = combined_df.sort_values('Tarih', ascending=False)
            else:
                combined_df = new_df
                combined_df = combined_df.sort_values('Tarih', ascending=False)

            # CSV dosyasına kaydet
            combined_df.to_csv(csv_path, index=False)
            print(f"Veriler başarıyla 'earthquakes.csv' dosyasına eklendi.")
            return combined_df
            
        except Exception as e:
            print(f"Hata oluştu: {str(e)}")
            return None
        
    except Exception as e:
        print(f"Hata oluştu: {str(e)}")
        return None

if __name__ == "__main__":
    get_kandilli_data()
