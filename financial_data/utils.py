import requests
import joblib
import time
import os
from datetime import datetime, timedelta
from django.conf import settings
from .models import StockData

API_KEY = 'UOU03LLUFXCSFK4J' 

def fetch_stock_data(symbol):
    today = datetime.now()
    start_date = today - timedelta(days=730)  # Approx. 2 years ago
    all_data = {}
    
    while today > start_date:
        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={API_KEY}&outputsize=full'
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for HTTP errors

            data = response.json()
            time_series = data.get('Time Series (Daily)', {})
            for date, metrics in time_series.items():
                # Store data only within the required date range
                if datetime.strptime(date, '%Y-%m-%d') < start_date:
                    break
                all_data[date] = metrics

            time.sleep(12)  # Sleep for a bit to avoid hitting rate limits

        except requests.exceptions.RequestException as e:
            # Log error and return status
            print(f"Error fetching data for {symbol}: {e}")
            return {'success': False, 'message': str(e)}

        today = today - timedelta(days=100)  # Fetch the next batch (last 100 days)

    # Save the data to the database
    for date, metrics in all_data.items():
        StockData.objects.update_or_create(
            symbol=symbol,
            date=date,
            defaults={
                'open_price': float(metrics['1. open']),
                'close_price': float(metrics['4. close']),
                'high_price': float(metrics['2. high']),
                'low_price': float(metrics['3. low']),
                'volume': int(metrics['5. volume']),
            }
        )

    return {'success': True, 'message': f"Data for {symbol} fetched successfully."}

def load_model():
    model_path = os.path.join(settings.BASE_DIR, 'models', 'stock_price_prediction.pkl')
    try:
        return joblib.load(model_path)
    except FileNotFoundError:
        print(f"Model file not found at {model_path}.")
        return None
    except Exception as e:
        print(f"Error loading model: {str(e)}")
        return None
