from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from users.serializers import RegisterSerializer, BalanceSerializer


class RegisterView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer


class BalanceView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        serializer = BalanceSerializer(
            {"balance": request.user.balance.balance}
        )
        return Response(serializer.data)
