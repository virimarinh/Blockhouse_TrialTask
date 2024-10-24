# Blockhouse_TrialTask

Block house Trial Task 
### **Fetch Financial Data**

- **API to Use**: Alpha Vantage (https://www.alphavantage.co/documentation/)
- **Data to Fetch**: Daily stock prices for a specific stock symbol (e.g., AAPL) over the past 2 years.
- **Required Fields**:
    - Open price
    - Close price
    - High price
    - Low price
    - Volume
- **Storage**: Store the fetched data in a PostgreSQL database. The table structure should be clear and optimized for querying, including timestamps for the financial data.

**Deliverables for this step**:

- Django view or background task that fetches the financial data.
- Proper database schema using Django ORM for storing the financial data.
- Code should include error handling (e.g., rate limits, network issues).

  ### 2. **Backtesting Module**

- **Goal**: Implement a basic backtesting strategy where users can input simple parameters, such as:
    - Initial investment amount
    - Buy when the stock price dips below a moving average (e.g., 50-day average).
    - Sell when the stock price goes above a different moving average (e.g., 200-day average).
- **Output**:
    - Calculate the return on investment based on these simple buy/sell rules.
    - Generate a performance summary including total return, max drawdown, and the number of trades executed.

**Deliverables for this step**:

- A Django view or API endpoint where users can input the backtesting parameters.
- Logic to fetch the stored historical data, apply the strategy, and return the backtest result.
- Test cases to validate the backtesting logic.

  ### 3. **Machine Learning Integration**

- **Pre-Trained Model Integration**:
    - You don’t need to build or train a new machine learning model from scratch. Instead, use a simple pre-trained machine learning model (such as a linear regression model) to predict future stock prices based on historical data.
    - The focus here is on integration, not ML development.
    - You can load the pre-trained model from a file (e.g., a `.pkl` file) and use it to generate predictions.
- **Where to Integrate**:
    - Implement a Django API endpoint that uses this pre-trained model to predict stock prices for the next 30 days based on the fetched historical data.
    - Predictions should be stored in the database alongside actual stock prices for comparison later.

**Deliverables for this step**:

- Django API endpoint that takes the stock symbol as input and returns the predicted stock prices for the next 30 days using the pre-trained model.
- Proper handling and storage of predictions alongside historical data.

  ### 4. **Report Generation**

- **Output**:
    - Generate a performance report after backtesting or after using the machine learning predictions.
    - The report should include the key financial metrics from the backtest and a visual comparison between the predicted and actual stock prices (use libraries like Matplotlib or Plotly for graphs).
- **Report Formats**:
    - The report should be available as downloadable PDFs and JSON responses via an API.

**Deliverables for this step**:

- A Django view or API endpoint that generates and returns the report.
- The report should include visualizations, key metrics, and predictions.
