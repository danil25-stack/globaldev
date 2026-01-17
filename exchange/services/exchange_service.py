import requests
from django.conf import settings
from django.db import transaction
from rest_framework.response import Response
from django.contrib.auth.models import AbstractBaseUser as User

from exchange.models import CurrencyExchange
from exchange.serializers import CurrencyExchangeResponseSerializer
from exchange.exceptions import (
    ExternalAPIError,
    NotEnoughBalance
)



class ExchangeService:
    """Service to handle currency exchange operations."""

    def __init__(self, cleaned_data: dict) -> None:
        self._to_currency = cleaned_data["currency_code"]
        self._user = cleaned_data["user"]

    def get_exchange_rate(self) -> Response:
        """Fetches the exchange rate from an external API."""
        raw_data = self._fetch_rate_to_uah(self._to_currency)
        rate = self._retrieve_rate(raw_data, self._to_currency)
        exchange_record = self._save_to_db(rate, settings.COST_PER_REQUEST)
        return self._prepare_response(exchange_record)  

    @transaction.atomic
    def _save_to_db(self, rate: float, cost: int) -> CurrencyExchange:
        """Saves the exchange rate record to the database."""
        self._subtract_user_balance(self._user, cost)
        return self._save_exchange_rate_to_db(
            user=self._user,
            currency_code=self._to_currency,
            rate=rate,
            cost=cost
        )

    def _prepare_response(
            self,
            exchange_record: CurrencyExchange
    ) -> dict:
        """Prepares the response data after a successful exchange."""
        serializer = CurrencyExchangeResponseSerializer(data={
            "currency_code": exchange_record.currency_code,
            "rate_to_uah": str(exchange_record.rate),
            "cost": settings.COST_PER_REQUEST,
            "balance_left": self._user.balance.balance,
        })
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=200)

    @staticmethod
    def _retrieve_rate(data: dict, currency_code: str) -> float:
        """Extracts the exchange rate to UAH from the API response data."""
        try:
            rate = data["conversion_rates"]["UAH"]
            if not isinstance(rate, (int, float)):
                raise ExternalAPIError(
                    f"Invalid rate type received for {currency_code}"
                )
            return float(rate)
        except (KeyError, TypeError) as e:
            raise ExternalAPIError(
                f"Malformed data received from API for {currency_code}: {e}"
            ) from e

    @staticmethod
    def _fetch_rate_to_uah(currency_code: str) -> dict:
        """Fetches exchange rate data from the external API."""
        api_key = settings.EXCHANGE_RATE_API_KEY
        url = settings.EXCHANGE_RATE_URL.format(
            api_key=api_key,
            currency_code=currency_code
        )
        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            return r.json()
        except requests.RequestException as e:
            raise ExternalAPIError(
                f"ExchangeRate API request failed: {e}"
            ) from e

    @staticmethod
    def _save_exchange_rate_to_db(
            user: User,
            currency_code: str,
            rate: float,
            cost: int
    ) -> CurrencyExchange:
        """Saves the exchange rate record to the database."""
        exchange_record = CurrencyExchange(
            user=user,
            currency_code=currency_code,
            rate=rate,
        )
        exchange_record.save()
        return exchange_record

    @staticmethod
    def _subtract_user_balance(user: User, amount: int) -> None:
        """Subtracts the specified amount from the user's balance."""
        if user.balance.balance < amount:
            raise NotEnoughBalance("Insufficient balance for this exchange.")
        user.balance.balance -= amount
        user.balance.save()
