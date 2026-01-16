from django.contrib import admin
from exchange.models import CurrencyExchange


@admin.register(CurrencyExchange)
class CurrencyExchangeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "currency_code",
        "rate",
        "created_at",
    )

    list_filter = (
        "currency_code",
        "created_at",
    )

    search_fields = (
        "user__id",
        "user__email",
        "currency_code",
    )

    ordering = ("-created_at",)

    readonly_fields = (
        "created_at",
    )

    list_select_related = ("user",)

    date_hierarchy = "created_at"

    fieldsets = (
        ("User info", {
            "fields": ("user",),
        }),
        ("Exchange data", {
            "fields": ("currency_code", "rate"),
        }),
        ("Metadata", {
            "fields": ("created_at",),
        }),
    )
