# backtesting_logic.py
def backtest_strategy(historical_data, initial_investment, buy_ma, sell_ma):
    cash = initial_investment
    shares = 0
    total_value_history = []

    for day in historical_data:
        price = day.close_price

        # Buy condition
        if price <= buy_ma and cash >= price:
            shares_to_buy = cash // price
            cash -= shares_to_buy * price
            shares += shares_to_buy
            print(f"Bought {shares_to_buy} shares at {price}. Cash remaining: {cash}")

        # Sell condition
        if price >= sell_ma and shares > 0:
            cash += shares * price
            print(f"Sold {shares} shares at {price}. Cash total: {cash}")
            shares = 0

        # Record total value (cash + value of shares held)
        total_value_history.append(cash + shares * price)

    return {
        'final_cash': cash,
        'total_return': cash - initial_investment,
        'total_value_history': total_value_history
    }
