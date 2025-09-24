import logging
from decimal import Decimal
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings

from .models import Payment
from .serializers import PaymentSerializer, PaymentInitSerializer
from .paystack import PaystackAPI

logger = logging.getLogger(__name__)

@api_view(['POST'])
def initialize_payment(request):
    """Initialize a Paystack payment with detailed logging"""
    serializer = PaymentInitSerializer(data=request.data)
    
    if not serializer.is_valid():
        logger.error(f"Serializer validation failed: {serializer.errors}")
        return Response({
            'success': False,
            'message': 'Invalid data',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        email = serializer.validated_data['email']
        amount = serializer.validated_data['amount']
        callback_url = serializer.validated_data.get('callback_url')

        logger.info(f"Initializing payment: {email}, Amount: {amount}")

        # Create payment record
        payment = Payment.objects.create(
            email=email,
            amount=amount,
            user=request.user if request.user.is_authenticated else None
        )

        logger.info(f"Payment record created: {payment.reference}")

        # Initialize Paystack transaction
        paystack_api = PaystackAPI()
        result = paystack_api.initialize_transaction(
            email=email,
            amount=float(amount),  # Convert Decimal to float for Paystack
            reference=payment.reference,
            callback_url=callback_url
        )
        
        logger.info(f"Paystack API response: {result}")
        
        if result.get('status'):
            payment.paystack_access_code = result['data']['access_code']
            payment.save()
            
            response_data = {
                'success': True,
                'message': 'Payment initialized successfully',
                'data': {
                    'reference': payment.reference,
                    'authorization_url': result['data']['authorization_url'],
                    'access_code': result['data']['access_code'],
                }
            }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            payment.status = 'failed'
            payment.save()
            error_msg = result.get('message', 'Unknown Paystack error')
            logger.error(f"Paystack initialization failed: {error_msg}")
            return Response({
                'success': False,
                'message': error_msg,
                'paystack_response': result
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"Unexpected error in initialize_payment: {str(e)}", exc_info=True)
        return Response({
            'success': False,
            'message': 'Internal server error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def verify_payment(request, reference):
    """Verify a payment with detailed logging"""
    try:
        payment = get_object_or_404(Payment, reference=reference)
        logger.info(f"Verifying payment: {reference}")
        
        paystack_api = PaystackAPI()
        result = paystack_api.verify_transaction(reference)
        
        logger.info(f"Paystack verification response: {result}")
        
        if result.get('status') and result['data']['status'] == 'success':
            payment.status = 'success'
            payment.paystack_transaction_id = result['data']['id']
            payment.save()
            
            serializer = PaymentSerializer(payment)
            logger.info(f"Payment verified successfully: {reference}")
            return Response({
                'success': True,
                'message': 'Payment verified successfully',
                'data': serializer.data
            })
        else:
            payment.status = 'failed'
            payment.save()
            error_msg = result.get('message', 'Verification failed')
            logger.error(f"Payment verification failed: {error_msg}")
            return Response({
                'success': False,
                'message': error_msg,
                'paystack_response': result
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"Unexpected error in verify_payment: {str(e)}", exc_info=True)
        return Response({
            'success': False,
            'message': 'Internal server error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
@api_view(['GET'])
def payment_list(request):
    """Get list of payments (optional: for authenticated users)"""
    payments = Payment.objects.all()

    # If you want to filter by user when authenticated
    if request.user.is_authenticated:
        payments = payments.filter(user=request.user)

    serializer = PaymentSerializer(payments, many=True)
    return Response({
        'success': True,
        'data': serializer.data
    })

@csrf_exempt
def paystack_webhook(request):
    """Handle Paystack webhooks"""
    if request.method == 'POST':
        # Verify webhook signature (important for security)
        # For production, implement signature verification

        import json
        payload = json.loads(request.body)

        event = payload.get('event')
        data = payload.get('data')

        if event == 'charge.success':
            reference = data.get('reference')
            try:
                payment = Payment.objects.get(reference=reference)
                payment.status = 'success'
                payment.paystack_transaction_id = data.get('id')
                payment.save()

                # Here you can trigger other actions like sending emails, updating orders, etc.
                print(f"Payment {reference} completed successfully via webhook")

            except Payment.DoesNotExist:
                pass

        return JsonResponse({'status': 'success'})

    return JsonResponse({'error': 'Method not allowed'}, status=405)
