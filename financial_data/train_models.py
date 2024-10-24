import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import joblib

# Load your historical data (ensure the CSV or data source exists)
# Make sure your dataset includes 'Open', 'Close', etc.
df = pd.read_csv('path_to_your_historical_data.csv')

# Prepare your features (X) and target (y)
df['Date'] = pd.to_datetime(df['Date'])  # Ensure the date is in datetime format
df.set_index('Date', inplace=True)
df['Target'] = df['Close'].shift(-1)  # Predicting the next day's closing price

# Drop the last row since it won't have a target value
df = df[:-1]

# Features and target
X = df[['Open', 'High', 'Low', 'Volume']]  # Use relevant features
y = df['Target']

# Split the dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Create a linear regression model
model = LinearRegression()
model.fit(X_train, y_train)

# Save the model to a .pkl file
joblib.dump(model, 'stock_price_predictor.pkl')
