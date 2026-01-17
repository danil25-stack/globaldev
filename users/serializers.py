from django.db import transaction
from rest_framework import serializers
from django.contrib.auth import get_user_model

from users.models import UserBalance


User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ("username", "password")

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("User with this username already exists.")
        return value

    @transaction.atomic
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        UserBalance.objects.create(user=user, balance=1000)
        return user


class BalanceSerializer(serializers.Serializer):
    balance = serializers.IntegerField(
        min_value=0
    )
