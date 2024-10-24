from django.db import models
from django.utils import timezone

# Create your models here.

class StockData(models.Model):
    symbol = models.CharField(max_length=10, verbose_name="Stock Symbol")
    date = models.DateField(verbose_name="Date")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Creation Timestamp") 
    open_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Open Price")
    close_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Close Price")
    high_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="High Price")
    low_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Low Price")
    volume = models.BigIntegerField(verbose_name="Volume")

    class Meta:
        unique_together = ('symbol', 'date')  # Ensure no duplicate entries for the same date
        ordering = ['date']  # Order by date

    def __str__(self):
        return f"{self.symbol} on {self.date}"


class StockPrediction(models.Model):
    symbol = models.CharField(max_length=10, verbose_name="Stock Symbol")
    date = models.DateField(verbose_name="Date")
    predicted_price = models.FloatField(verbose_name="Predicted Price")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Prediction Timestamp")

    class Meta:
        unique_together = ('symbol', 'date')  # Ensure no duplicate predictions for the same date
        ordering = ['date']  # Order by date

    def __str__(self):
        return f"Prediction for {self.symbol} on {self.date}: {self.predicted_price}"

    def get_prediction_for_date(self, target_date):
        """
        Retrieve the predicted price for a specific date.

        Args:
            target_date (date): The date for which to retrieve the prediction.

        Returns:
            float or None: The predicted price if found, else None.
        """
        try:
            prediction = StockPrediction.objects.get(symbol=self.symbol, date=target_date)
            return prediction.predicted_price
        except StockPrediction.DoesNotExist:
            return None
