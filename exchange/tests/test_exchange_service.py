import pytest
from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework.response import Response

from exchange.models import CurrencyExchange
from exchange.services import ExchangeService
from exchange.exceptions import ExternalAPIError, NotEnoughBalance


User = get_user_model()


@pytest.fixture
def user(db):
    u = User.objects.create_user(username="u1", password="pass12345")

    from users.models import UserBalance
    UserBalance.objects.create(user=u, balance=100)

    u.refresh_from_db()
    return u


@pytest.fixture
def cleaned_data(user):
    return {"currency_code": "USD", "user": user}


@pytest.mark.django_db
def test_get_exchange_rate_success(cleaned_data, settings, monkeypatch):
    settings.COST_PER_REQUEST = 5

    monkeypatch.setattr(
        ExchangeService,
        "_fetch_rate_to_uah",
        staticmethod(lambda currency_code: {"conversion_rates": {"UAH": 39.5}}),
    )

    svc = ExchangeService(cleaned_data)
    resp = svc.get_exchange_rate()

    assert isinstance(resp, Response)
    assert resp.status_code == 200
    assert resp.data["currency_code"] == "USD"
    assert Decimal(str(resp.data["rate_to_uah"])) == Decimal("39.5")
    assert resp.data["cost"] == 5
    assert resp.data["balance_left"] == 95

    assert CurrencyExchange.objects.count() == 1
    ex = CurrencyExchange.objects.first()
    assert ex.currency_code == "USD"
    assert Decimal(str(ex.rate)) == Decimal("39.5")


@pytest.mark.django_db
def test_get_exchange_rate_not_enough_balance_atomic(cleaned_data, settings, monkeypatch):
    settings.COST_PER_REQUEST = 1000

    monkeypatch.setattr(
        ExchangeService,
        "_fetch_rate_to_uah",
        staticmethod(lambda currency_code: {"conversion_rates": {"UAH": 40}}),
    )

    svc = ExchangeService(cleaned_data)

    with pytest.raises(NotEnoughBalance):
        svc.get_exchange_rate()

    assert CurrencyExchange.objects.count() == 0
    cleaned_data["user"].refresh_from_db()
    assert cleaned_data["user"].balance.balance == 100


@pytest.mark.django_db
def test_fetch_rate_to_uah_request_exception(settings, cleaned_data, monkeypatch):
    settings.COST_PER_REQUEST = 1

    
    monkeypatch.setattr(
        ExchangeService,
        "_fetch_rate_to_uah",
        staticmethod(
            lambda currency_code: (_ for _ in ()).throw(ExternalAPIError("boom"))
        ),
    )

    svc = ExchangeService(cleaned_data)
    with pytest.raises(ExternalAPIError):
        svc.get_exchange_rate()

    assert CurrencyExchange.objects.count() == 0


@pytest.mark.django_db
def test_fetch_rate_to_uah_http_error(settings, cleaned_data, monkeypatch):
    settings.COST_PER_REQUEST = 1

    monkeypatch.setattr(
        ExchangeService,
        "_fetch_rate_to_uah",
        staticmethod(
            lambda currency_code: (_ for _ in ()).throw(ExternalAPIError("403"))
        ),
    )

    svc = ExchangeService(cleaned_data)
    with pytest.raises(ExternalAPIError):
        svc.get_exchange_rate()

    assert CurrencyExchange.objects.count() == 0


@pytest.mark.parametrize(
    "data",
    [
        {},
        {"conversion_rates": {}},
        {"conversion_rates": {"UAH": "39.5"}},
        {"conversion_rates": None},
    ],
)
def test_retrieve_rate_invalid_data(data):
    with pytest.raises(ExternalAPIError):
        ExchangeService._retrieve_rate(data, "USD")


def test_retrieve_rate_ok():
    rate = ExchangeService._retrieve_rate({"conversion_rates": {"UAH": 38}}, "USD")
    assert isinstance(rate, float)
    assert rate == 38.0


@pytest.mark.django_db
def test_subtract_user_balance_ok(user):
    ExchangeService._subtract_user_balance(user, 10)
    user.refresh_from_db()
    assert user.balance.balance == 90


@pytest.mark.django_db
def test_subtract_user_balance_not_enough(user):
    with pytest.raises(NotEnoughBalance):
        ExchangeService._subtract_user_balance(user, 999)
    user.refresh_from_db()
    assert user.balance.balance == 100
