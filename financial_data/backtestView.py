from django.views import View
from django.http import JsonResponse
from .models import StockData
from .backtesting_logic import backtest_strategy

class BacktestView(View):
    def post(self, request):
        # Get parameters from the request body
        try:
            initial_investment = float(request.POST.get('initial_investment'))
            buy_ma = float(request.POST.get('buy_ma'))
            sell_ma = float(request.POST.get('sell_ma'))
            symbol = request.POST.get('symbol')

            # Fetch historical data for the specified symbol
            historical_data = StockData.objects.filter(symbol=symbol).order_by('date')

            # Check if historical data is available
            if not historical_data.exists():
                return JsonResponse({'error': 'No historical data found for the specified symbol.'}, status=404)

            # Call the backtest strategy
            results = backtest_strategy(historical_data, initial_investment, buy_ma, sell_ma)

            # Return results as a JSON response
            return JsonResponse(results)

        except ValueError:
            return JsonResponse({'error': 'Invalid input. Please provide numeric values for investment and moving averages.'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
