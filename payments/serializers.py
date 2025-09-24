from decimal import Decimal
from rest_framework import serializers
from .models import Payment

class PaymentInitSerializer(serializers.Serializer):
    email = serializers.EmailField()
    amount = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        min_value=Decimal('0.01')  # Use Decimal instead of float
    )
    callback_url = serializers.URLField(required=False)

class PaymentSerializer(serializers.ModelSerializer):
    authorization_url = serializers.CharField(read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'email', 'amount', 'reference', 'status',
            'paystack_transaction_id', 'created_at', 'authorization_url'
        ]
        read_only_fields = ['reference', 'status', 'paystack_transaction_id', 'created_at']