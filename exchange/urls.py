from django.urls import path

from exchange.views import CurrencyView, HistoryView


urlpatterns = [
    path("currency/", CurrencyView.as_view(), name="currency"),
    path("history/", HistoryView.as_view(), name="history"),
]
