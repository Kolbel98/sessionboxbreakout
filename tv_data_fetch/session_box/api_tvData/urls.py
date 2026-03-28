from django.urls import path
from .views import PriceDataView, BacktestView

urlpatterns = [
    path("price-data/", PriceDataView.as_view(), name="price-data"),
    path("backtest/", BacktestView.as_view(), name="backtest"),
]
