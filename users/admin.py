from django.contrib import admin
from users.models import UserBalance


@admin.register(UserBalance)
class UserBalanceAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "balance",
    )

    search_fields = (
        "user__username",
        "user__email",
        "user__id",
    )

    list_select_related = ("user",)

    ordering = ("user__username",)

    fieldsets = (
        ("User", {
            "fields": ("user",),
        }),
        ("Balance", {
            "fields": ("balance",),
        }),
    )
