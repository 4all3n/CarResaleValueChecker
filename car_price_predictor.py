import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib
import os
from flask import Flask, render_template, request, jsonify


DATA_FILE = 'dataset.csv' 
MODEL_FILE = 'car_model.joblib'
COLUMNS_FILE = 'model_columns.joblib'
CURRENT_YEAR = 2025 

#Flask App Initialization
app = Flask(__name__)

# --- Your Existing Model Logic (Copied from your script) ---

def train_and_save_model():
    """
    This function performs the following steps:
    1. Loads the dataset.
    2. Preprocesses the data and engineers new features.
    3. Trains a RandomForestRegressor model.
    4. Saves the trained model and the data columns to files.
    """
    print("--- Training and Saving Model ---")

    # --- 1. Load Data ---
    print(f"Loading data from {DATA_FILE}...")
    try:
        df = pd.read_csv(DATA_FILE)
    except FileNotFoundError:
        print(f"CRITICAL ERROR: Data file '{DATA_FILE}' not found.")
        print("Please make sure the dataset is in the same folder as app.py")
        return False

    # --- 2. Preprocess Data & Feature Engineering ---
    print("Preprocessing data and engineering features...")
    df['Age'] = CURRENT_YEAR - df['year']
    df['Brand'] = df['name'].apply(lambda x: x.split(' ')[0])
    df.drop(columns=['name', 'year'], inplace=True)
    
    # Handle potential missing values in selling_price before training
    df_processed = df.dropna(subset=['selling_price'])
    
    df_processed = pd.get_dummies(df_processed, columns=['fuel', 'seller_type', 'transmission', 'owner', 'Brand'], drop_first=True)

    # --- 3. Train Model ---
    print("Training the model...")
    X = df_processed.drop(columns=['selling_price'])
    y = df_processed['selling_price']

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    print("Model training complete.")

    # --- 4. Save the Model and Columns ---
    print(f"Saving model to {MODEL_FILE}...")
    joblib.dump(model, MODEL_FILE)

    print(f"Saving data columns to {COLUMNS_FILE}...")
    joblib.dump(X.columns.tolist(), COLUMNS_FILE) 

    print("--- Model and columns saved successfully! ---")
    return True # Indicate success

def predict_price(user_input):
    """
    Predicts the price of a car based on user input.
    (This is identical to your original function)
    """
    print("\n--- Making a New Prediction ---")

    try:
        model = joblib.load(MODEL_FILE)
        model_columns = joblib.load(COLUMNS_FILE)
    except FileNotFoundError:
        print("Model files not found. Prediction failed.")
        return None

    # Process User Input
    input_df = pd.DataFrame([user_input])
    
    # Perform the EXACT SAME feature engineering
    input_df['Age'] = CURRENT_YEAR - input_df['year']
    input_df['Brand'] = input_df['name'].apply(lambda x: x.split(' ')[0])
    
    # Drop columns that are not features
    # Note: 'name' and 'year' are in the input dict, so we must drop them
    input_df.drop(columns=['name', 'year'], inplace=True)

    input_processed = pd.get_dummies(input_df, columns=['fuel', 'seller_type', 'transmission', 'owner', 'Brand'])

    # Align Columns
    final_input = input_processed.reindex(columns=model_columns, fill_value=0)

    # Make Prediction
    prediction = model.predict(final_input)
    return prediction[0]

# --- Flask API Routes ---

@app.route('/')
def home():
    """
    Serves the main HTML page.
    Flask will look for 'index.html' in the 'templates' folder.
    """
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict_api():
    """
    Receives car data from the web form, processes it,
    and returns a prediction as JSON.
    """
    # Get data from the form (sent as JSON by our JavaScript)
    data = request.get_json()

    # --- Critical: Convert string numbers from form to integers ---
    # The form sends everything as text, but our model needs numbers
    try:
        data['year'] = int(data['year'])
        data['km_driven'] = int(data['km_driven'])
    except ValueError:
        return jsonify({'error': 'Invalid input for year or km_driven. Please enter numbers.'}), 400
    except KeyError:
         return jsonify({'error': 'Missing form data.'}), 400

    # Call your original prediction function
    prediction = predict_price(data)

    if prediction is not None:
        # Send the prediction back to the webpage in JSON format
        return jsonify({'prediction': prediction})
    else:
        return jsonify({'error': 'Model prediction failed.'}), 500

# --- Main execution ---
if __name__ == "__main__":
    # Check if the model files exist. If not, train and save a new one.
    model_exists = os.path.exists(MODEL_FILE) and os.path.exists(COLUMNS_FILE)
    
    if not model_exists:
        print("Model not found. Starting training process...")
        success = train_and_save_model()
        if not success:
            print("Exiting due to training failure. Please check data file.")
            exit()
    else:
        print("Model already exists. Skipping training.")
    
    # Start the Flask web server
    print("Starting Flask server... Access your app at http://127.0.0.1:5000")
    app.run(debug=True)

