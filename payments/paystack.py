import requests
from django.conf import settings
from django.core.exceptions import ValidationError

class PaystackAPI:
    def __init__(self):
        self.secret_key = settings.PAYSTACK_SECRET_KEY
        self.public_key = settings.PAYSTACK_PUBLIC_KEY
        self.base_url = settings.PAYSTACK_BASE_URL
        self.headers = {
            'Authorization': f'Bearer {self.secret_key}',
            'Content-Type': 'application/json',
        }

    def initialize_transaction(self, email, amount, reference, callback_url=None):
        """Initialize a Paystack transaction"""
        amount_in_kobo = int(amount * 100)  # Paystack expects amount in kobo
        
        payload = {
            'email': email,
            'amount': amount_in_kobo,
            'reference': reference,
        }
        
        if callback_url:
            payload['callback_url'] = callback_url

        try:
            response = requests.post(
                f'{self.base_url}/transaction/initialize',
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ValidationError(f"Paystack API error: {str(e)}")

    def verify_transaction(self, reference):
        """Verify a Paystack transaction"""
        try:
            response = requests.get(
                f'{self.base_url}/transaction/verify/{reference}',
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ValidationError(f"Paystack API error: {str(e)}")

    def create_subaccount(self, business_name, account_number, bank_code, percentage_charge):
        """Create a subaccount for split payments"""
        payload = {
            'business_name': business_name,
            'settlement_bank': bank_code,
            'account_number': account_number,
            'percentage_charge': percentage_charge,
        }
        
        try:
            response = requests.post(
                f'{self.base_url}/subaccount',
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ValidationError(f"Paystack API error: {str(e)}")
