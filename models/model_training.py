import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import mean_squared_error, accuracy_score
import pickle

def create_features(df):
    df['SonAy_DepremSayisi'] = df.groupby('Konum').rolling(
        window='30D', on='Tarih_Saat')['Buyukluk'].count().reset_index(0, drop=True)
    df['SonAy_OrtBuyukluk'] = df.groupby('Konum').rolling(
        window='30D', on='Tarih_Saat')['Buyukluk'].mean().reset_index(0, drop=True)
    df['SonAy_MaxBuyukluk'] = df.groupby('Konum').rolling(
        window='30D', on='Tarih_Saat')['Buyukluk'].max().reset_index(0, drop=True)
    df['SonAy_MinBuyukluk'] = df.groupby('Konum').rolling(
        window='30D', on='Tarih_Saat')['Buyukluk'].min().reset_index(0, drop=True)
    df['SonAy_StdBuyukluk'] = df.groupby('Konum').rolling(
        window='30D', on='Tarih_Saat')['Buyukluk'].std().reset_index(0, drop=True)

    df = df.sort_values('Tarih_Saat')
    df['OncekiDepremZamani'] = df.groupby('Konum')['Tarih_Saat'].shift(1)
    df['DepremAraligi'] = (df['Tarih_Saat'] - df['OncekiDepremZamani']).dt.total_seconds() / 3600

    df['SonAy_OrtAralik'] = df.groupby('Konum')['DepremAraligi'].rolling(window=30).mean().reset_index(0, drop=True)
    df['SonAy_MaxAralik'] = df.groupby('Konum')['DepremAraligi'].rolling(window=30).max().reset_index(0, drop=True)
    df['SonAy_MinAralik'] = df.groupby('Konum')['DepremAraligi'].rolling(window=30).min().reset_index(0, drop=True)

    datetime_cols = df.select_dtypes(include=['datetime64[ns]']).columns
    df[datetime_cols] = df[datetime_cols].fillna(pd.NaT)
    non_datetime_cols = df.columns.difference(datetime_cols)
    df[non_datetime_cols] = df[non_datetime_cols].fillna(0)

    return df

def create_time_category(hours):
    if hours <= 6:
        return 0
    elif hours <= 12:
        return 1
    elif hours <= 24:
        return 2
    elif hours <= 72:
        return 3
    else:
        return 4

def load_and_preprocess_data(filepath):
    df = pd.read_csv(filepath)
    df['Tarih_Saat'] = pd.to_datetime(df['Tarih_Saat'], format='%Y-%m-%d %H:%M:%S')
    le = LabelEncoder()
    df['Konum_Encoded'] = le.fit_transform(df['Konum'])
    df = create_features(df)

    # LabelEncoder'ı kaydet
    with open('C:/Users/alpba/Desktop/YapayZekaSon1/models/label_encoder.pkl', 'wb') as file:
        pickle.dump(le, file)

    return df, le

def train_models(df):
    features = [
        'Konum_Encoded', 'SonAy_DepremSayisi', 'SonAy_OrtBuyukluk', 
        'SonAy_MaxBuyukluk', 'SonAy_MinBuyukluk', 'SonAy_StdBuyukluk',
        'SonAy_OrtAralik', 'SonAy_MaxAralik', 'SonAy_MinAralik'
    ]

    X = df[features].fillna(0)
    y_magnitude = df['Buyukluk']
    df['ZamanKategorisi'] = df['DepremAraligi'].apply(create_time_category)
    y_time = df['ZamanKategorisi']

    X_train, X_test, y_mag_train, y_mag_test, y_time_train, y_time_test = train_test_split(
        X, y_magnitude, y_time, test_size=0.15, random_state=42
    )

    magnitude_model = RandomForestRegressor(
        n_estimators=200, 
        max_depth=15,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42
    )

    time_model = RandomForestClassifier(
        n_estimators=200,
        max_depth=15,
        min_samples_split=5,
        min_samples_leaf=2,
        class_weight='balanced',
        random_state=42
    )

    magnitude_model.fit(X_train, y_mag_train)
    time_model.fit(X_train, y_time_train)

    return magnitude_model, time_model, X_test, y_mag_test, y_time_test

def evaluate_models(magnitude_model, time_model, X_test, y_mag_test, y_time_test):
    mag_predictions = magnitude_model.predict(X_test)
    time_predictions = time_model.predict(X_test)

    print("Büyüklük Modeli MSE:", mean_squared_error(y_mag_test, mag_predictions))
    print("Zaman Modeli Doğruluk:", accuracy_score(y_time_test, time_predictions))

def predict_next_earthquake(magnitude_model, time_model, location, df):
    with open('C:/Users/alpba/Desktop/YapayZekaSon1/models/label_encoder.pkl', 'rb') as file:
        encoder = pickle.load(file)

    location_encoded = encoder.transform([location])[0]
    last_month = df[df['Konum'] == location].tail(30)
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

    magnitude_pred = magnitude_model.predict(features)[0]
    time_category = time_model.predict(features)[0]

    time_ranges = {
        0: "0-6 saat içinde",
        1: "6-12 saat içinde",
        2: "12-24 saat içinde",
        3: "1-3 gün içinde",
        4: "3+ gün içinde"
    }
    return magnitude_pred, time_ranges[time_category]

def main():
    filepath = 'C:/Users/alpba/Desktop/YapayZekaSon1/data/updated_earthquakes.csv'
    df, le = load_and_preprocess_data(filepath)
    magnitude_model, time_model, X_test, y_mag_test, y_time_test = train_models(df)
    evaluate_models(magnitude_model, time_model, X_test, y_mag_test, y_time_test)

    location = 'KAHRAMANMARAŞ'
    magnitude_pred, time_pred = predict_next_earthquake(magnitude_model, time_model, location, df)
    print(f"{location} için tahmin:")
    print(f"Beklenen deprem büyüklüğü: {magnitude_pred:.1f}")
    print(f"Tahmini gerçekleşme zamanı: {time_pred}")

    with open('C:/Users/alpba/Desktop/YapayZekaSon1/models/magnitude_model.pkl', 'wb') as file:
        pickle.dump(magnitude_model, file)
    with open('C:/Users/alpba/Desktop/YapayZekaSon1/models/time_model.pkl', 'wb') as file:
        pickle.dump(time_model, file)

if __name__ == "__main__":
    main()
