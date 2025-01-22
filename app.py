import requests
import sys
from datetime import datetime

def display_earthquakes(earthquakes):
    """Deprem verilerini düzenli bir şekilde göster"""
    print("\n{:<20} {:<15} {:<10}".format("Tarih/Saat", "Konum", "Büyüklük"))
    print("-" * 45)
    for eq in earthquakes:
        date = datetime.strptime(eq['Tarih_Saat'], "%Y-%m-%d %H:%M:%S")
        formatted_date = date.strftime("%d-%m-%Y %H:%M")
        print("{:<20} {:<15} {:<10.1f}".format(
            formatted_date,
            eq['Konum'],
            eq['Buyukluk']
        ))

def get_largest_earthquakes():
    """En büyük 5 depremi getir"""
    try:
        response = requests.get('http://localhost:5000/api/largest-earthquakes')
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'success':
                print("\n=== En Büyük 5 Deprem ===")
                display_earthquakes(data['data'])
            else:
                print("Hata:", data.get('message', 'Bilinmeyen bir hata oluştu'))
        else:
            print(f"Hata: API yanıt kodu {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("Hata: API'ye bağlanılamadı. API'nin çalıştığından emin olun.")
    except Exception as e:
        print(f"Hata oluştu: {str(e)}")

def get_earthquakes_by_location(location):
    """Belirli bir konumdaki en büyük 5 depremi getir"""
    try:
        response = requests.get(f'http://localhost:5000/api/earthquakes-by-location?location={location}')
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'success':
                print(f"\n=== {location} İlindeki En Büyük 5 Deprem ===")
                display_earthquakes(data['data'])
            else:
                print("Hata:", data.get('message', 'Bilinmeyen bir hata oluştu'))
        elif response.status_code == 404:
            print(f"Hata: {location} konumunda deprem kaydı bulunamadı")
        else:
            print(f"Hata: API yanıt kodu {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("Hata: API'ye bağlanılamadı. API'nin çalıştığından emin olun.")
    except Exception as e:
        print(f"Hata oluştu: {str(e)}")

def predict_next_earthquake():
    """Belirli bir konum için deprem tahmini yap"""
    try:
        location = input("Konum giriniz (örn: IZMIR): ").upper()

        response = requests.post(
            'http://localhost:5000/api/predict-next-earthquake',
            json={'location': location}
        )

        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'success':
                print(f"\n=== {data['location']} İçin Deprem Tahmini ===")
                print(f"Tahmini Büyüklük: {data['predicted_magnitude']}")
                print(f"Tahmini Gerçekleşme Süresi: {data['predicted_time_range']}")
                print("\nNOT: Bu tahminler sadece geçmiş verilere dayalı istatistiksel bir yaklaşımdır.")
                print("Kesin sonuçlar vermez ve gerçek deprem tahmini için kullanılamaz.")
            else:
                print("Hata:", data.get('message', 'Bilinmeyen bir hata oluştu'))
        else:
            print(f"Hata: API yanıt kodu {response.status_code}")

    except requests.exceptions.ConnectionError:
        print("Hata: API'ye bağlanılamadı. API'nin çalıştığından emin olun.")
    except Exception as e:
        print(f"Hata oluştu: {str(e)}")

def main_menu():
    """Ana menüyü göster ve kullanıcı seçimlerini işle"""
    while True:
        print("\n=== Deprem Verileri Uygulaması ===")
        print("1. En Büyük 5 Depremi Göster")
        print("2. Tek Konuma Göre Deprem Ara")
        print("3. Deprem Tahmini Yap")
        print("4. Çıkış")

        choice = input("\nSeçiminiz (1-4): ")

        if choice == '1':
            get_largest_earthquakes()
        elif choice == '2':
            location = input("Konum giriniz (örn: IZMIR): ").upper()
            get_earthquakes_by_location(location)
        elif choice == '3':
            predict_next_earthquake()
        elif choice == '4':
            print("Program sonlandırılıyor...")
            sys.exit(0)
        else:
            print("Geçersiz seçim! Lütfen 1-4 arasında bir sayı giriniz.")

if __name__ == "__main__":
    main_menu()
