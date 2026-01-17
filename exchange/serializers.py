from rest_framework import serializers

from users.models import UserBalance
from exchange.models import CurrencyExchange


class CurrencyRequestSerializer(serializers.Serializer):
    currency_code = serializers.CharField(max_length=10)

    def validate_currency_code(self, value: str) -> str:
        value = value.strip().upper()
        if not value.isalpha():
            raise serializers.ValidationError(
                "currency_code must contain only letters, like 'USD'"
            )
        if len(value) not in (3,):
            raise serializers.ValidationError(
                "currency_code must be 3 letters, like 'USD'"
            )
        return value
    
    def validate(self, attrs):
        request = self.context.get("request")
        positive_balance = UserBalance.objects.filter(
            user=request.user,
            balance__gt=0,
        ).exists()
        if not positive_balance:
            raise serializers.ValidationError("User does not have enough balance.")
        attrs["user"] = request.user
        return attrs


class CurrencyExchangeResponseSerializer(serializers.Serializer):
    currency_code = serializers.CharField(max_length=10)
    rate_to_uah = serializers.DecimalField(max_digits=20, decimal_places=6)
    cost = serializers.IntegerField()
    balance_left = serializers.DecimalField(max_digits=20, decimal_places=2)


class CurrencyExchangeHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CurrencyExchange
        fields = (
            "id",
            "currency_code",
            "rate",
            "created_at",
        )
