# Car Resale Value Checker

A small Flask-based UI that sends car details to a trained model and returns an estimated resale price.

This repository contains a minimal web UI (Tailwind-based) and the model artifacts used by the backend.

---

## Files of interest

- `car_price_predictor.py` — Flask app / inference endpoint (expected to expose `POST /predict`).
- `car_model.joblib` — trained model file required by the predictor.
- `model_columns.joblib` — list/columns used by the model.
- `dataset.csv` — the dataset used to create the model and used to derive allowed option values.
- `templates/index.html` — the web UI. I updated this file to be modern and dataset-aware.

---

## Quick setup (Windows PowerShell)

1. Create and activate a virtual environment

```powershell
# from the project Test folder
python -m venv .venv
# activate
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies

```powershell
pip install -r requirements.txt
```

3. Run the Flask app

(If `car_price_predictor.py` defines `app` and a `if __name__ == '__main__'` runner.)

```powershell
# from the Test folder
$env:FLASK_APP = "car_price_predictor.py"
$env:FLASK_ENV = "development"
flask run --host=127.0.0.1 --port=5000
```

If your `car_price_predictor.py` is runnable as `python car_price_predictor.py`, you can use that instead:

```powershell
python car_price_predictor.py
```

4. Open the UI

Visit: http://127.0.0.1:5000/ in your browser.

---

## UI notes & changes

- The UI is in `templates/index.html` and uses Tailwind for styling.
- Select/dropdown options (Fuel, Seller Type, Transmission, Owner) were limited to the values present in the dataset. The selected values include: Petrol, Diesel, CNG, LPG; Individual, Dealer, Trustmark Dealer; Manual, Automatic; First/Second/Third/Fourth & Above Owner.
- The Car Model input now spans the full form width so long model names are visible.
- The dropdown arrows were standardized using an inline SVG positioned inside a `relative` wrapper to avoid browser-specific misalignment.

If you want selects to be dynamically generated from the dataset (instead of hard-coded in the HTML), I can add a small `/meta` endpoint (or inject the values into the HTML template) so the UI always reflects your dataset automatically.

---

## API contract (what the UI expects)

- Request: POST `/predict` with JSON body containing at least the following keys:
  - `name` (string)
  - `year` (number)
  - `km_driven` (number)
  - `fuel` (string)
  - `seller_type` (string)
  - `transmission` (string)
  - `owner` (string)

- Response: JSON with a numeric `prediction` field, e.g.

```json
{ "prediction": 450000 }
```

The UI formats `prediction` as INR currency.

---

## Troubleshooting

- If you get errors about missing model files, make sure `car_model.joblib` and `model_columns.joblib` are placed in the same folder as `car_price_predictor.py` or that the app points to the correct paths.
- If the UI posts to `/predict` but nothing happens, check the Flask server logs for exceptions.

