from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from exchange.serializers import (
    CurrencyRequestSerializer,
    CurrencyExchangeHistorySerializer
)
from exchange.models import CurrencyExchange
from exchange.services import ExchangeService
from exchange.filters import CurrencyExchangeFilter
from exchange.exceptions import NotEnoughBalance, ExternalAPIError


class CurrencyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request) -> Response:
        s = CurrencyRequestSerializer(
            data=request.data, context={"request": request}
        )
        s.is_valid(raise_exception=True)
        try:
            return ExchangeService(s.validated_data).get_exchange_rate()
        except NotEnoughBalance as e:
            return Response(
                {"detail": str(e)}, status=status.HTTP_402_PAYMENT_REQUIRED
            )
        except ExternalAPIError as e:
            return Response(
                {"detail": str(e)}, status=status.HTTP_502_BAD_GATEWAY
            )


class HistoryView(ListAPIView):
    filter_backends = [DjangoFilterBackend]
    filterset_class = CurrencyExchangeFilter
    serializer_class = CurrencyExchangeHistorySerializer

    def get_queryset(self):
        return CurrencyExchange.objects.filter(user=self.request.user)
