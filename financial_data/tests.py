from django.test import TestCase
from .models import StockData  
from .backtesting_logic import backtest_strategy  

class BacktestStrategyTests(TestCase):
    
    def setUp(self):
        # Clear existing data to prevent unique constraint violations
        StockData.objects.all().delete()

        # Create sample stock data for testing
        StockData.objects.create(symbol='AAPL', date='2024-10-01', open_price=150, close_price=155, high_price=160, low_price=148, volume=1000000)
        StockData.objects.create(symbol='AAPL', date='2024-10-02', open_price=155, close_price=153, high_price=157, low_price=150, volume=1200000)
        StockData.objects.create(symbol='AAPL', date='2024-10-03', open_price=153, close_price=158, high_price=159, low_price=152, volume=1300000)

    def test_backtest_strategy(self):
        initial_investment = 1000
        buy_ma = 154
        sell_ma = 157
        
        historical_data = StockData.objects.filter(symbol='AAPL').order_by('date')
        
        results = backtest_strategy(historical_data, initial_investment, buy_ma, sell_ma)

        self.assertIsInstance(results, dict)
        self.assertIn('final_cash', results)
        self.assertIn('total_return', results)
        self.assertGreaterEqual(results['final_cash'], 0)
    
    def test_backtest_with_no_data(self):
        # Clear existing data to prevent unique constraint violations
        StockData.objects.all().delete()

        historical_data = []  # No data
        initial_investment = 1000
        buy_ma = 50
        sell_ma = 200

        results = backtest_strategy(historical_data, initial_investment, buy_ma, sell_ma)

        self.assertEqual(results['final_cash'], initial_investment)
        self.assertEqual(results['total_return'], 0)
        self.assertEqual(results['total_value_history'], [])

    def test_backtest_with_no_trades(self):
        # Clear existing data to prevent unique constraint violations
        StockData.objects.all().delete()

        # Create stock data where no trades should occur
        historical_data = [
            {'symbol': 'AAPL', 'date': '2024-10-01', 'open_price': 100, 'close_price': 100, 'high_price': 100, 'low_price': 100, 'volume': 1000},
            {'symbol': 'AAPL', 'date': '2024-10-02', 'open_price': 100, 'close_price': 100, 'high_price': 100, 'low_price': 100, 'volume': 1000},
            {'symbol': 'AAPL', 'date': '2024-10-03', 'open_price': 100, 'close_price': 100, 'high_price': 100, 'low_price': 100, 'volume': 1000},
        ]

        # Use bulk_create to add the stock data to the database
        StockData.objects.bulk_create([
            StockData(**data) for data in historical_data
        ])

        initial_investment = 1000
        buy_ma = 90
        sell_ma = 110

        results = backtest_strategy(StockData.objects.filter(symbol='AAPL'), initial_investment, buy_ma, sell_ma)

        self.assertEqual(results['final_cash'], initial_investment)
        self.assertEqual(results['total_return'], 0)
        self.assertEqual(results['total_value_history'], [1000] * len(historical_data))

    def test_backtest_with_various_investments(self):
        # Clear existing data to prevent unique constraint violations
        StockData.objects.all().delete()

        # Create stock data for the test
        historical_data = [
            {'symbol': 'AAPL', 'date': '2024-10-01', 'open_price': 150, 'close_price': 153, 'high_price': 155, 'low_price': 150, 'volume': 1000},  # Buy condition
            {'symbol': 'AAPL', 'date': '2024-10-02', 'open_price': 155, 'close_price': 158, 'high_price': 160, 'low_price': 153, 'volume': 1000},  # Sell condition
        ]

        # Use bulk_create to add the stock data to the database
        StockData.objects.bulk_create([
            StockData(**data) for data in historical_data
        ])

        initial_investment = 1000
        results = backtest_strategy(StockData.objects.filter(symbol='AAPL'), initial_investment, buy_ma=153, sell_ma=158)  # Adjusted moving averages
        
        expected_return = 1030  # Based on buying 6 shares at 153 and selling them at 158
        
        self.assertEqual(results['final_cash'], expected_return)
        self.assertEqual(results['total_return'], expected_return - initial_investment)
