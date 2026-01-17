import django_filters as filters

from exchange.models import CurrencyExchange


class CurrencyExchangeFilter(filters.FilterSet):
    """FilterSet for filtering CurrencyExchange records."""

    currency = filters.CharFilter(
        field_name="currency_code",lookup_expr="iexact"
    )
    date_from = filters.DateFilter(
        field_name="created_at", lookup_expr="date__gte"
    )
    date_to = filters.DateFilter(
        field_name="created_at", lookup_expr="date__lte"
    )

    class Meta:
        model = CurrencyExchange
        fields = ["currency", "date_from", "date_to"]
