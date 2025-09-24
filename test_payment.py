import os
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paystack_api.settings')
django.setup()

from payments.paystack import PaystackAPI

def test_paystack_connection():
    """Test Paystack API connection"""
    paystack = PaystackAPI()
    
    # Test with a small amount
    try:
        result = paystack.initialize_transaction(
            email="test@example.com",
            amount=1.00,  # 1 NGN
            reference="test_ref_123"
        )
        print("Paystack API Test Result:")
        print(result)
    except Exception as e:
        print(f"Paystack API Test Failed: {e}")

if __name__ == "__main__":
    test_paystack_connection()
