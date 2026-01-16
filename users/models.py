from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class UserBalance(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="balance"
    )
    balance = models.IntegerField(default=1000)

    def __str__(self) -> str:
        return f"{self.user.username}: {self.balance}"
