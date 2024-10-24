"""
URL configuration for Blockhouse_TrialTask project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from financial_data.views import home, FetchStockDataView, PredictStockPriceView, GenerateReportView, GeneratePDFReportView

urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('fetch-stock-data/<str:symbol>/', FetchStockDataView.as_view(), name='fetch_stock_data'),
    path('predict-stock-price/<str:symbol>/', PredictStockPriceView.as_view(), name='predict_stock_price'),
    path('report/<str:symbol>/', GenerateReportView.as_view(), name='generate_report'),
    path('report/<str:symbol>/pdf/', GeneratePDFReportView.as_view(), name='generate_pdf_report'),  # Unique path for PDF
]
