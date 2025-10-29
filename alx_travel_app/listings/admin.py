from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("booking_reference", "transaction_id", "amount", "currency", "status", "created_at")
    readonly_fields = ("created_at", "updated_at",)
    search_fields = ("booking_reference", "transaction_id", "user__username", "user__email")

