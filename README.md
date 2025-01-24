# Earthquake Prediction and Analysis Application

This project was developed to process, analyze, and predict the magnitude and timing of future earthquakes in Turkey. By leveraging **machine learning and data processing techniques**, it provides earthquake insights and predictions via an API and CLI interface.

## Project Features

### 1. **Data Processing and Preparation**
- Earthquake data is fetched from the **Kandilli Observatory** website.
- Each earthquake record is matched with its corresponding province using geographic coordinates.
- Processed data is stored in the `updated_earthquakes.csv` file.

### 2. **Machine Learning Models**
The project includes two core machine learning models:
- **Earthquake Magnitude Prediction Model**: Predicts the magnitude of a future earthquake based on past data.
  - Algorithm: `RandomForestRegressor`
- **Earthquake Time Category Prediction Model**: Classifies the expected time range of a future earthquake.
  - Algorithm: `RandomForestClassifier`

After training, models are saved in `.pkl` format:
- `magnitude_model.pkl`
- `time_model.pkl`

### 3. **API**
The project provides a **Flask-based REST API**:
- **GET /api/largest-earthquakes**: Returns the top 5 largest earthquakes.
- **GET /api/earthquakes-by-location?location=LOCATION**: Returns the top 5 largest earthquakes for a specific location.
- **POST /api/predict-next-earthquake**: Predicts the magnitude and expected time range of a future earthquake.

### 4. **CLI (Command Line Interface)**
- A user-friendly **CLI application** allows users to:
  - View the largest earthquakes.
  - Analyze earthquakes for a specific location.
  - Get predictions for future earthquakes' magnitude and timing.

---

## Project Structure

```
📂 Project Folder
├── 📂 data
│   ├── earthquakes.csv
│   ├── updated_earthquakes.csv
│   ├── turkiye_il_koordinatlari.json
├── 📂 models
│   ├── label_encoder.pkl
│   ├── magnitude_model.pkl
│   ├── time_model.pkl
│   ├── model_training.py
├── 📂 scripts
│   ├── api.py
│   ├── data_processing.py
│   ├── data_scrapper.py
├── app.py
└── README.md
```

---

## Installation

### 1. Install Required Libraries
Install the necessary Python libraries using:
```bash
pip install -r requirements.txt
```

### 2. Update the Data
Run the `data_scrapper.py` script to fetch the latest earthquake data from the **Kandilli Observatory**:
```bash
python scripts/data_scrapper.py
```

### 3. Process the Data
Run the `data_processing.py` script to process the fetched data and match it with provinces:
```bash
python scripts/data_processing.py
```

### 4. Train the Models
Train the prediction models by running the `model_training.py` script:
```bash
python models/model_training.py
```

### 5. Start the API
Run the `api.py` script to launch the Flask-based API:
```bash
python scripts/api.py
```

### 6. Run the CLI Application
Use the `app.py` script to start the CLI application:
```bash
python app.py
```

---

## API Usage
### 1. Get the Largest Earthquakes
```bash
GET /api/largest-earthquakes
```
### 2. Get Earthquakes by Location
```bash
GET /api/earthquakes-by-location?location=IZMIR
```
### 3. Predict Future Earthquake
```bash
POST /api/predict-next-earthquake
Body: { "location": "IZMIR" }
```

---

## Example CLI Outputs
### 1. Top 5 Largest Earthquakes
```
=== Top 5 Largest Earthquakes ===
Date/Time           Location        Magnitude
---------------------------------------------
25-12-2024 16:28    AKDENIZ         5.4
25-12-2024 15:13    KASTAMONU       5.0
...
```
### 2. Future Earthquake Prediction
```
=== Prediction for IZMIR ===
Predicted Magnitude: 4.3
Predicted Time Range: Within 1-3 days
NOTE: These predictions are based solely on historical data and statistical models.
They are not definitive and should not be used for actual earthquake forecasting.
```

---

## Contribution
To contribute to this project:
1. Fork this repository.
2. Create a new branch: `git checkout -b new-feature`
3. Commit your changes: `git commit -m 'Add new feature'`
4. Push the branch: `git push origin new-feature`
5. Open a Pull Request.

---

## License
This project is licensed under the MIT License. For more details, see the [LICENSE](LICENSE) file.

---

## Contact
For any questions or suggestions, feel free to reach out:
- **Email:** example@example.com
- **LinkedIn:** [My Profile](https://linkedin.com/in/example)

