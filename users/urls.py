from django.urls import path

from users.views import BalanceView, RegisterView


urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("balance/", BalanceView.as_view(), name="balance"),
]
