import requests
import time
import joblib
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for plotting
import matplotlib.pyplot as plt
import io
import base64
from django.views import View
import numpy as np
from decimal import Decimal
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, FileResponse
from .models import StockData, StockPrediction
import logging
import os
from django.conf import settings
from datetime import datetime, timedelta
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

API_KEY = 'UOU03LLUFXCSFK4J' 
logger = logging.getLogger(__name__)

# Home view for testing
def home(request):
    return HttpResponse("Welcome to the Stock Price Predictor!")

# Function to fetch stock data from Alpha Vantage API
def fetch_stock_data(symbol):
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={API_KEY}&outputsize=full'
    logger.info(f"Fetching data for {symbol} from URL: {url}")

    try:
        response = requests.get(url)
        logger.info(f"Response Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            logger.info(f"Data fetched successfully for {symbol}: {data}")

            time_series = data.get('Time Series (Daily)', {})
            if not time_series:
                logger.error(f"No time series data found for {symbol}.")
                return {'success': False, 'message': 'No time series data found.', 'status': 200}

            # Process and store data
            for date, metrics in time_series.items():
                if all(key in metrics for key in ['1. open', '4. close', '2. high', '3. low', '5. volume']):
                    StockData.objects.update_or_create(
                        symbol=symbol,
                        date=date,
                        defaults={
                            'open_price': Decimal(metrics['1. open']),
                            'close_price': Decimal(metrics['4. close']),
                            'high_price': Decimal(metrics['2. high']),
                            'low_price': Decimal(metrics['3. low']),
                            'volume': int(metrics['5. volume']),
                        }
                    )
                    logger.info(f"Stored data for {symbol} on {date}")
                else:
                    logger.warning(f"Missing data for {symbol} on {date}")
        else:
            logger.error(f"Error fetching data for {symbol}: {response.status_code}")
            return {'success': False, 'message': f'Error fetching data: {response.status_code}', 'status': response.status_code}

        time.sleep(12)  # Avoid hitting the API rate limit
        return {'success': True, 'message': f'Data for {symbol} has been fetched.', 'status': 200}

    except requests.exceptions.RequestException as e:
        logger.error(f"Error occurred while fetching data for {symbol}: {str(e)}")
        return {'success': False, 'message': f"Error occurred: {str(e)}", 'status': 500}


class FetchStockDataView(View):
    def get(self, request, symbol):
        result = fetch_stock_data(symbol)
        return JsonResponse({'success': result['success'], 'message': result['message']}, status=result['status'])


class PredictStockPriceView(View):
    def get(self, request, symbol):
        print("Starting prediction for symbol:", symbol)
        model_path = os.path.join(settings.BASE_DIR, 'models', 'stock_price_predictor.pkl')

        try:
            print("Loading model from:", model_path)
            model = joblib.load(model_path)  # Load the model using joblib
            print("Model loaded successfully. Type:", type(model))  # Debugging output
        except FileNotFoundError:
            return JsonResponse({'error': 'Model file not found.'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

        # Fetch historical data for the given stock symbol
        historical_data = StockData.objects.filter(symbol=symbol).order_by('date')
        print("Fetched historical data for:", symbol)

        if not historical_data.exists():
            return JsonResponse({'symbol': symbol, 'error': 'No historical data available.'}, status=404)

        # Prepare features for prediction
        features_array = self.prepare_features(historical_data)
        print("Shape of features:", features_array.shape)

        # Generate future features for the next 30 days based on the last known features
        last_features = features_array[-1]  # Get the last entry from the features array
        future_features = self.generate_future_features(last_features)
        print("Generated future features for prediction:", future_features)

        # Combine historical features with future features for prediction
        all_features = np.vstack((features_array, future_features))

        # Convert to DataFrame with the same columns as the training set
        feature_columns = ['Open', 'High', 'Low', 'Volume']  # Adjust as needed
        all_features_df = pd.DataFrame(all_features, columns=feature_columns)

        try:
            predicted_prices = model.predict(all_features_df)

            return JsonResponse({'symbol': symbol, 'predicted_prices': predicted_prices.tolist()}, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    def prepare_features(self, historical_data):
        """
        Prepare features from historical stock data.
        """
        features = []
        for record in historical_data:
            features.append([
                record.open_price,
                record.high_price,
                record.low_price,
                record.volume
            ])
        return np.array(features)

    def generate_future_features(self, last_features):
        """
        Generate future features based on the last known features.
        """
        future_features = np.tile(last_features, (30, 1))  # Create 30 rows of future features
        return future_features


class GenerateReportView(View):
    def get(self, request, symbol):
        # Fetch historical stock data
        historical_data = StockData.objects.filter(symbol=symbol).order_by('date')

        if not historical_data.exists():
            return JsonResponse({'error': 'No historical data available for this symbol.'}, status=404)

        # Predict future prices
        predicted_prices = self.predict_prices(historical_data)

        # Generate the report data
        report_data = {
            'symbol': symbol,
            'dates': [entry.date for entry in historical_data],
            'historical_prices': [entry.close_price for entry in historical_data],
            'predicted_prices': predicted_prices
        }

        # Generate a plot of historical vs. predicted prices
        plot_path = self.generate_plot_file(report_data)

        # Create PDF report
        response = self.generate_pdf(report_data, plot_path)

        return response

    def predict_prices(self, historical_data):
        """
        Generate predicted prices using a pre-trained model.
        """
        model_path = os.path.join(settings.BASE_DIR, 'models', 'stock_price_predictor.pkl')
        
        # Load the model
        try:
            model = joblib.load(model_path)
        except FileNotFoundError:
            return {'error': 'Model file not found.'}
        except Exception as e:
            return {'error': f'Error loading model: {str(e)}'}

        # Prepare features from historical data
        features_array = self.prepare_features(historical_data)
        
        # Generate future features for the next 30 days
        future_features = self.generate_future_features(features_array[-1])

        # Combine historical features with future features for prediction
        all_features = np.vstack((features_array, future_features))

        # Make predictions
        predicted_prices = model.predict(all_features)

        return predicted_prices[-30:].tolist()  # Return the last 30 predicted prices

    def prepare_features(self, historical_data):
        """
        Prepare features from historical stock data.
        """
        features = []
        for entry in historical_data:
            features.append([
                float(entry.open_price),  # Open price
                float(entry.high_price),  # High price
                float(entry.low_price),   # Low price
                int(entry.volume)         # Volume
            ])
        return np.array(features)

    def generate_future_features(self, last_features):
        """
        Generate future stock price features for the next 30 days based on the last known features.
        """
        future_features = []
        for i in range(30):  # Generate features for the next 30 days
            new_open = last_features[0] * (1 + np.random.uniform(-0.02, 0.02))  # 2% variation
            new_high = last_features[1] * (1 + np.random.uniform(-0.02, 0.02))
            new_low = last_features[2] * (1 + np.random.uniform(-0.02, 0.02))
            new_volume = int(last_features[3] * (1 + np.random.uniform(-0.1, 0.1)))  # 10% variation
            
            future_features.append([new_open, new_high, new_low, new_volume])
        
        return np.array(future_features)

    def generate_plot_file(self, report_data):
        """
        Generates the stock price comparison plot and saves it to a file.
        Returns the file path for the saved image.
        """
        plt.figure(figsize=(10, 6))
        plt.plot(report_data['dates'], report_data['historical_prices'], label='Historical Prices', color='blue')
        plt.plot(report_data['dates'][-30:], report_data['predicted_prices'], label='Predicted Prices', color='orange')
        plt.title(f"Stock Prices for {report_data['symbol']}")
        plt.xlabel("Date")
        plt.ylabel("Price")
        plt.xticks(rotation=45)
        plt.legend()
        plt.tight_layout()

        # Save the plot to a file
        plot_file_path = os.path.join(settings.MEDIA_ROOT, f'{report_data["symbol"]}_stock_prices.png')
        plt.savefig(plot_file_path)
        plt.close()  # Close the plot to free memory

        return plot_file_path

    def generate_pdf(self, report_data, plot_path):
        """
        Generates a PDF report with historical and predicted prices, including a plot.
        """
        pdf_file_path = os.path.join(settings.MEDIA_ROOT, f'{report_data["symbol"]}_report.pdf')

        # Create a PDF document
        c = canvas.Canvas(pdf_file_path, pagesize=letter)
        c.drawString(100, 750, f"Stock Price Report for {report_data['symbol']}")
        c.drawString(100, 730, f"Report Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        c.drawString(100, 700, "Historical Prices:")
        for i, price in enumerate(report_data['historical_prices']):
            c.drawString(100, 680 - i * 15, f"{report_data['dates'][i]}: {price}")

        c.drawString(100, 620, "Predicted Prices for Next 30 Days:")
        for i, price in enumerate(report_data['predicted_prices']):
            c.drawString(100, 600 - i * 15, f"Day {i + 1}: {price}")

        # Draw the plot
        c.drawImage(plot_path, 100, 400, width=400, height=300)  # Adjust the position and size as needed

        c.save()  # Save the PDF document
        logger.info(f"PDF report generated: {pdf_file_path}")

        return FileResponse(open(pdf_file_path, 'rb'), as_attachment=True, filename=os.path.basename(pdf_file_path))


class GeneratePDFReportView(View):
    def get(self, request, symbol):
        """
        Generate a PDF report for the specified stock symbol.
        """
        historical_data = StockData.objects.filter(symbol=symbol).order_by('date')

        if not historical_data.exists():
            return JsonResponse({'error': 'No historical data available for this symbol.'}, status=404)

        # Prepare report data
        report_data = {
            'symbol': symbol,
            'dates': [entry.date for entry in historical_data],
            'historical_prices': [entry.close_price for entry in historical_data],
        }

        # Generate the plot file
        plot_path = self.generate_plot_file(report_data)

        # Create PDF report
        pdf_response = self.generate_pdf(report_data, plot_path)

        return pdf_response

    def generate_plot_file(self, report_data):
        """
        Generates the stock price comparison plot and saves it to a file.
        Returns the file path for the saved image.
        """
        plt.figure(figsize=(10, 6))
        plt.plot(report_data['dates'], report_data['historical_prices'], label='Historical Prices', color='blue')
        plt.title(f"Stock Prices for {report_data['symbol']}")
        plt.xlabel("Date")
        plt.ylabel("Price")
        plt.xticks(rotation=45)
        plt.legend()
        plt.tight_layout()

        # Save the plot to a file
        plot_file_path = os.path.join(settings.MEDIA_ROOT, f'{report_data["symbol"]}_stock_prices.png')
        plt.savefig(plot_file_path)
        plt.close()  # Close the plot to free memory

        return plot_file_path

    def generate_pdf(self, report_data, plot_path):
        """
        Generates a PDF report with historical stock prices and includes a plot.
        """
        pdf_file_path = os.path.join(settings.MEDIA_ROOT, f'{report_data["symbol"]}_report.pdf')

        # Create a PDF document
        c = canvas.Canvas(pdf_file_path, pagesize=letter)
        c.drawString(100, 750, f"Stock Price Report for {report_data['symbol']}")
        c.drawString(100, 730, f"Report Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        c.drawString(100, 700, "Historical Prices:")
        
        # Set the initial y-coordinate for historical prices
        y = 680
        for i, price in enumerate(report_data['historical_prices']):
            c.drawString(100, y, f"{report_data['dates'][i]}: {price}")
            y -= 18  # Increased spacing for historical prices

        c.drawString(100, y - 20, "Predicted Prices for Next 30 Days:")
        y -= 40  # Leave some space before the predicted prices section

        for i, price in enumerate(report_data['predicted_prices']):
            c.drawString(100, y, f"Day {i + 1}: {price}")
            y -= 18  # Increased spacing for predicted prices

        # Draw the plot
        c.drawImage(plot_path, 100, y - 300, width=400, height=300)  # Adjust the position and size as needed

        c.save()  # Save the PDF document
        logger.info(f"PDF report generated: {pdf_file_path}")

        return FileResponse(open(pdf_file_path, 'rb'), as_attachment=True, filename=os.path.basename(pdf_file_path))
