from rest_framework import serializers, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.conf import settings

from .models import Payment
from apps.orders.models import Order


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_payment_intent(request):
    """Create a Stripe PaymentIntent for an order."""
    order_id = request.data.get('order_id')
    try:
        order = Order.objects.get(pk=order_id, user=request.user)
    except Order.DoesNotExist:
        return Response({'success': False, 'message': 'Order not found.'}, status=404)

    try:
        import stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY
        intent = stripe.PaymentIntent.create(
            amount=int(order.total * 100),  # in cents
            currency='egp',
            metadata={'order_id': str(order.id), 'order_number': order.order_number},
        )
        payment, _ = Payment.objects.get_or_create(
            order=order,
            defaults={
                'user': request.user,
                'amount': order.total,
                'method': 'stripe',
                'stripe_payment_intent_id': intent.id,
            }
        )
        return Response({
            'success': True,
            'client_secret': intent.client_secret,
            'payment_intent_id': intent.id,
        })
    except Exception as e:
        return Response({'success': False, 'message': str(e)}, status=400)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def stripe_webhook(request):
    """Handle Stripe webhook events."""
    import stripe
    stripe.api_key = settings.STRIPE_SECRET_KEY
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        return Response({'error': 'Invalid signature'}, status=400)

    if event['type'] == 'payment_intent.succeeded':
        pi = event['data']['object']
        try:
            payment = Payment.objects.get(stripe_payment_intent_id=pi['id'])
            payment.status = 'succeeded'
            payment.stripe_charge_id = pi.get('latest_charge', '')
            payment.save()
            payment.order.payment_status = 'paid'
            payment.order.status = 'confirmed'
            payment.order.save()
        except Payment.DoesNotExist:
            pass

    elif event['type'] == 'payment_intent.payment_failed':
        pi = event['data']['object']
        try:
            payment = Payment.objects.get(stripe_payment_intent_id=pi['id'])
            payment.status = 'failed'
            payment.failure_message = pi.get('last_payment_error', {}).get('message', '')
            payment.save()
        except Payment.DoesNotExist:
            pass

    return Response({'received': True})