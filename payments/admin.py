# Register your models here.
from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['reference', 'email', 'amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['reference', 'email']
    readonly_fields = ['reference', 'created_at', 'updated_at']
