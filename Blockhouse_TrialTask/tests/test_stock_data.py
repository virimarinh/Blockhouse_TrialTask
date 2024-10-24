from django.test import TestCase
from django.urls import reverse
from financial_data.models import StockData
from unittest.mock import patch

class StockDataFetchTestCase(TestCase):
    def setUp(self):
        self.symbol = 'AAPL'

    @patch('requests.get')
    def test_fetch_stock_data_success(self, mock_get):
        # Mock the response from the requests.get call
        mock_response = {
            'Time Series (Daily)': {
                '2024-10-20': {
                    '1. open': '85.00',
                    '2. high': '86.00',
                    '3. low': '84.00',
                    '4. close': '85.50',
                    '5. volume': '100000'
                }
            }
        }
        
        # Set the mock response to be returned by requests.get
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response
        
        # Call the view that fetches stock data
        response = self.client.get(reverse('fetch_stock_data', args=[self.symbol]))
        
        # Check that the response is successful
        self.assertEqual(response.status_code, 200)
        
        # Validate that data is stored correctly in the database
        self.assertTrue(StockData.objects.filter(symbol=self.symbol).exists())
        
        # Fetch the stored data to validate the contents
        stored_data = StockData.objects.get(symbol=self.symbol)
        self.assertEqual(stored_data.open_price, 85.00)
        self.assertEqual(stored_data.high_price, 86.00)
        self.assertEqual(stored_data.low_price, 84.00)
        self.assertEqual(stored_data.close_price, 85.50)
        self.assertEqual(stored_data.volume, 100000)

    @patch('requests.get')
    def test_fetch_stock_data_no_data(self, mock_get):
        # Mock the response to simulate no time series data
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            'Time Series (Daily)': {}
        }
        
        # Call the function or view that fetches stock data
        response = self.client.get(reverse('fetch_stock_data', args=[self.symbol]))
        
        # Check that the response is successful
        self.assertEqual(response.status_code, 200)
        
        # Validate that no data is stored in the database
        self.assertFalse(StockData.objects.filter(symbol=self.symbol).exists())
        
        # Validate the response message
        self.assertEqual(response.json(), {'success': False, 'message': 'No time series data found.'})

    @patch('requests.get')
    def test_fetch_stock_data_api_error(self, mock_get):
        # Mock the API error response
        mock_get.return_value.status_code = 500  # Simulate server error
        
        # Call the function or view that fetches stock data
        response = self.client.get(reverse('fetch_stock_data', args=[self.symbol]))
        
        # Check that the response status code is 500
        self.assertEqual(response.status_code, 500)
        
        # Validate that no data is stored in the database
        self.assertFalse(StockData.objects.filter(symbol=self.symbol).exists())
        
        # Validate the response message
        self.assertEqual(response.json(), {'success': False, 'message': 'Error fetching data: 500'})
