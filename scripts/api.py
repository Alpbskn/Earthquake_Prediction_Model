from flask import Flask, jsonify, request
import pandas as pd
import os
import pickle

app = Flask(__name__)

def get_csv_path():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    return os.path.join(project_root, 'YapayZekaSon1', 'data', 'updated_earthquakes.csv')

def get_model_path(model_name):
    current_dir = "C:\\Users\\alpba\\Desktop\\YapayZekaSon1"
    model_dir = os.path.join(current_dir, 'models')
    return os.path.join(model_dir, f'{model_name}.pkl')

@app.route('/api/largest-earthquakes', methods=['GET'])
def get_largest_earthquakes():
    try:
        csv_path = get_csv_path()
        df = pd.read_csv(csv_path)
        largest_earthquakes = df.nlargest(5, 'Buyukluk')[['Tarih_Saat', 'Konum', 'Buyukluk']]
        result = largest_earthquakes.to_dict('records')
        return jsonify({
            'status': 'success',
            'data': result
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/earthquakes-by-location', methods=['GET'])
def get_earthquakes_by_location():
    try:
        location = request.args.get('location', '').upper()
        if not location:
            return jsonify({
                'status': 'error',
                'message': 'Konum parametresi gerekli'
            }), 400

        csv_path = get_csv_path()
        df = pd.read_csv(csv_path)
        location_earthquakes = df[df['Konum'] == location]

        if len(location_earthquakes) == 0:
            return jsonify({
                'status': 'error',
                'message': f'"{location}" konumunda deprem kaydı bulunamadı'
            }), 404

        largest_in_location = location_earthquakes.nlargest(5, 'Buyukluk')[['Tarih_Saat', 'Konum', 'Buyukluk']]
        result = largest_in_location.to_dict('records')

        return jsonify({
            'status': 'success',
            'location': location,
            'count': len(result),
            'data': result
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/predict-next-earthquake', methods=['POST'])
@app.route('/api/predict-next-earthquake', methods=['POST'])
def predict_next_earthquake():
    try:
        data = request.get_json()
        location = data.get('location', '').upper()

        if not location:
            return jsonify({
                'status': 'error',
                'message': 'Konum bilgisi gerekli'
            }), 400

        csv_path = get_csv_path()
        df = pd.read_csv(csv_path)
        df['Tarih_Saat'] = pd.to_datetime(df['Tarih_Saat'], format='%Y-%m-%d %H:%M:%S')

        # LabelEncoder'ı yükle
        with open('C:/Users/alpba/Desktop/YapayZekaSon1/models/label_encoder.pkl', 'rb') as file:
            encoder = pickle.load(file)

        if location not in encoder.classes_:
            return jsonify({
                'status': 'error',
                'message': f'"{location}" konumu tanımlı değil'
            }), 404

        location_encoded = encoder.transform([location])[0]
        last_month = df[df['Konum'] == location].tail(30)

        # DepremAraligi sütununu oluştur
        last_month['OncekiDepremZamani'] = last_month['Tarih_Saat'].shift(1)
        last_month['DepremAraligi'] = (last_month['Tarih_Saat'] - last_month['OncekiDepremZamani']).dt.total_seconds() / 3600
        print("Step 10: DepremAraligi sütunu oluşturuldu:", last_month[['Tarih_Saat', 'DepremAraligi']])

        # Özellikleri oluştur
        features = pd.DataFrame({
            'Konum_Encoded': [location_encoded],
            'SonAy_DepremSayisi': [len(last_month)],
            'SonAy_OrtBuyukluk': [last_month['Buyukluk'].mean()],
            'SonAy_MaxBuyukluk': [last_month['Buyukluk'].max()],
            'SonAy_MinBuyukluk': [last_month['Buyukluk'].min()],
            'SonAy_StdBuyukluk': [last_month['Buyukluk'].std()],
            'SonAy_OrtAralik': [last_month['DepremAraligi'].mean()],
            'SonAy_MaxAralik': [last_month['DepremAraligi'].max()],
            'SonAy_MinAralik': [last_month['DepremAraligi'].min()]
        }).fillna(0)
        print("Step 11: Özellikler oluşturuldu:", features)

        # Model dosyalarını yükle
        magnitude_model_path = get_model_path('magnitude_model')
        time_model_path = get_model_path('time_model')

        with open(magnitude_model_path, 'rb') as file:
            magnitude_model = pickle.load(file)
        with open(time_model_path, 'rb') as file:
            time_model = pickle.load(file)

        # Tahmin yap
        magnitude_pred = magnitude_model.predict(features)[0]
        time_category = time_model.predict(features)[0]
        print("Step 12: Tahminler yapıldı - Magnitude:", magnitude_pred, "Time Category:", time_category)

        time_ranges = {
            0: "0-6 saat içinde",
            1: "6-12 saat içinde",
            2: "12-24 saat içinde",
            3: "1-3 gün içinde",
            4: "3+ gün içinde"
        }

        return jsonify({
            'status': 'success',
            'location': location,
            'predicted_magnitude': round(magnitude_pred, 2),
            'predicted_time_range': time_ranges[time_category]
        })

    except Exception as e:
        print("Hata oluştu:", str(e))  # Hata mesajını logla
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500




if __name__ == '__main__':
    app.run(debug=True, port=5000)
