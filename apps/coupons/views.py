from decimal import Decimal
from rest_framework import serializers, generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from .models import Coupon


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = '__all__'


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def validate_coupon(request):
    code = request.data.get('code', '').strip().upper()

    try:
        order_total = Decimal(str(request.data.get('order_total', 0)))
    except Exception:
        return Response({'success': False, 'message': 'Invalid order total.'}, status=400)

    try:
        coupon = Coupon.objects.get(code=code, is_active=True)
    except Coupon.DoesNotExist:
        return Response({'success': False, 'message': 'Invalid coupon code.'}, status=400)

    # Basic validity checks (works for both guests and logged-in users)
    now = timezone.now()
    if coupon.starts_at and now < coupon.starts_at:
        return Response({'success': False, 'message': 'This coupon is not yet active.'}, status=400)
    if coupon.expires_at and now > coupon.expires_at:
        return Response({'success': False, 'message': 'This coupon has expired.'}, status=400)
    if coupon.usage_limit and coupon.used_count >= coupon.usage_limit:
        return Response({'success': False, 'message': 'This coupon has reached its usage limit.'}, status=400)
    if order_total < coupon.minimum_order_amount:
        return Response({
            'success': False,
            'message': f'Minimum order amount is {coupon.minimum_order_amount} EGP.'
        }, status=400)

    # Per-user limit check only for logged-in users
    if request.user.is_authenticated and coupon.usage_limit_per_user:
        from .models import CouponUsage
        user_usage = CouponUsage.objects.filter(coupon=coupon, user=request.user).count()
        if user_usage >= coupon.usage_limit_per_user:
            return Response({'success': False, 'message': 'You have already used this coupon.'}, status=400)

    # Calculate discount
    discount = coupon.calculate_discount(order_total)

    return Response({
        'success': True,
        'message': 'Coupon applied successfully.',
        'discount_amount': str(round(discount, 2)),
        'coupon': {
            'id': coupon.id,
            'code': coupon.code,
            'discount_type': coupon.discount_type,
            'discount_value': str(coupon.discount_value),
            'discount_amount': str(round(discount, 2)),
        }
    })


# Admin
class AdminCouponListCreateView(generics.ListCreateAPIView):
    serializer_class = CouponSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Coupon.objects.all()


class AdminCouponDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CouponSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Coupon.objects.all()