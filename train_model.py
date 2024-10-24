import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import joblib  # Use joblib for model saving

# Step 1: Create a mock dataset (or load your historical data)
data = {
    'Open': [150, 152, 153, 154, 155, 157, 158, 159, 160, 162],
    'High': [155, 157, 158, 159, 160, 162, 163, 164, 165, 167],
    'Low': [149, 151, 152, 153, 154, 156, 157, 158, 159, 161],
    'Close': [154, 156, 157, 158, 159, 161, 162, 163, 164, 166],
    'Volume': [1000, 1500, 1200, 1300, 1600, 1100, 1400, 1150, 1800, 1700]
}

# Create a DataFrame
df = pd.DataFrame(data)

# Step 2: Prepare the feature set (X) and target variable (y)
X = df[['Open', 'High', 'Low', 'Volume']]  # Features
y = df['Close']  # Target variable

# Step 3: Train the model
model = LinearRegression()
model.fit(X, y)

# Step 4: Save the model
model_path = 'C:\\Users\\Viri\\Blockhouse_TrialTask\\models\\stock_price_predictor.pkl'
joblib.dump(model, model_path)  # Ensure you save the model, not an array

print("Model trained and saved as stock_price_predictor.pkl")
