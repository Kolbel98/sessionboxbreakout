from django.urls import path
from .views import PriceDataView

urlpatterns = [
    path("price-data/", PriceDataView.as_view(), name="price-data"),
]
