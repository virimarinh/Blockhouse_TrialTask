# Generated by Django 5.1.2 on 2024-10-22 15:56

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('financial_data', '0002_stockprediction'),
    ]

    operations = [
        migrations.AddField(
            model_name='stockdata',
            name='timestamp',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2024, 10, 22, 15, 54, 57, 788726, tzinfo=datetime.timezone.utc), verbose_name='Creation Timestamp'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='stockprediction',
            name='timestamp',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2024, 10, 22, 15, 56, 43, 565993, tzinfo=datetime.timezone.utc), verbose_name='Prediction Timestamp'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='stockdata',
            name='close_price',
            field=models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Close Price'),
        ),
        migrations.AlterField(
            model_name='stockdata',
            name='date',
            field=models.DateField(verbose_name='Date'),
        ),
        migrations.AlterField(
            model_name='stockdata',
            name='high_price',
            field=models.DecimalField(decimal_places=2, max_digits=10, verbose_name='High Price'),
        ),
        migrations.AlterField(
            model_name='stockdata',
            name='low_price',
            field=models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Low Price'),
        ),
        migrations.AlterField(
            model_name='stockdata',
            name='open_price',
            field=models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Open Price'),
        ),
        migrations.AlterField(
            model_name='stockdata',
            name='symbol',
            field=models.CharField(max_length=10, verbose_name='Stock Symbol'),
        ),
        migrations.AlterField(
            model_name='stockdata',
            name='volume',
            field=models.BigIntegerField(verbose_name='Volume'),
        ),
        migrations.AlterField(
            model_name='stockprediction',
            name='date',
            field=models.DateField(verbose_name='Date'),
        ),
        migrations.AlterField(
            model_name='stockprediction',
            name='predicted_price',
            field=models.FloatField(verbose_name='Predicted Price'),
        ),
        migrations.AlterField(
            model_name='stockprediction',
            name='symbol',
            field=models.CharField(max_length=10, verbose_name='Stock Symbol'),
        ),
    ]
