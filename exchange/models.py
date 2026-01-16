from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class CurrencyExchange(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="exchange_requests",
    )
    currency_code = models.CharField(max_length=10)
    rate = models.DecimalField(max_digits=18, decimal_places=8)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "currency_code", "created_at"]),
        ]

    def __str__(self):
        return f"{self.user_id} {self.currency_code} {self.rate} ; {self.created_at}"
