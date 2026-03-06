from decimal import Decimal
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db import transaction
from django.db.models import F

from .models import Order, OrderItem, OrderStatusHistory
from .serializers import (
    OrderSerializer, OrderListSerializer, CreateOrderSerializer, UpdateOrderStatusSerializer
)
from apps.cart.models import Cart
from apps.users.models import Address
from apps.coupons.models import Coupon
from apps.products.models import Product, ProductVariant


class OrderListView(generics.ListAPIView):
    serializer_class = OrderListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])  # Guests can checkout too
def create_order(request):
    serializer = CreateOrderSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    user = request.user if request.user.is_authenticated else None

    # ── Get cart items ──────────────────────────────────────────────
    # For authenticated users: try backend cart first, then fall back to request items
    # For guests: always use items from request body (localStorage cart)

    cart_items_data = []  # Will hold dicts with product info

    if user:
        try:
            cart = Cart.objects.get(user=user)
            backend_items = cart.items.select_related('product', 'variant').all()
            if backend_items.exists():
                cart_items_data = list(backend_items)
                use_backend_cart = True
            else:
                use_backend_cart = False
        except Cart.DoesNotExist:
            use_backend_cart = False
    else:
        use_backend_cart = False

    # If no backend cart, read items from request body
    if not use_backend_cart:
        raw_items = request.data.get('items', [])
        if not raw_items:
            return Response({'success': False, 'message': 'Cart is empty.'}, status=400)
        cart_items_data = raw_items

    if not cart_items_data:
        return Response({'success': False, 'message': 'Cart is empty.'}, status=400)

    # ── Resolve shipping address ────────────────────────────────────
    shipping_data = {}
    if data.get('address_id') and user:
        try:
            address = Address.objects.get(pk=data['address_id'], user=user)
            shipping_data = {
                'shipping_name': address.full_name,
                'shipping_phone': address.phone,
                'shipping_address_line1': address.address_line1,
                'shipping_address_line2': address.address_line2,
                'shipping_city': address.city,
                'shipping_state': address.state,
                'shipping_postal_code': address.postal_code,
                'shipping_country': address.country,
            }
        except Address.DoesNotExist:
            return Response({'success': False, 'message': 'Address not found.'}, status=404)
    else:
        required = ['shipping_name', 'shipping_phone', 'shipping_address_line1', 'shipping_city']
        for field in required:
            if not data.get(field):
                return Response({'success': False, 'message': f'{field} is required.'}, status=400)
        shipping_data = {k: data.get(k, '') for k in [
            'shipping_name', 'shipping_phone', 'shipping_address_line1',
            'shipping_address_line2', 'shipping_city', 'shipping_state',
            'shipping_postal_code', 'shipping_country'
        ]}

    # ── Calculate totals ────────────────────────────────────────────
    if use_backend_cart:
        subtotal = sum(item.line_total for item in cart_items_data)
    else:
        subtotal = Decimal('0')
        for item in cart_items_data:
            price = Decimal(str(item.get('price', 0)))
            qty = int(item.get('quantity', 1))
            subtotal += price * qty

    discount_amount = Decimal('0')
    coupon_code = ''
    coupon = None

    if data.get('coupon_code'):
        try:
            coupon = Coupon.objects.get(code=data['coupon_code'].upper(), is_active=True)
            discount_amount = coupon.calculate_discount(subtotal)
            coupon_code = coupon.code
        except Coupon.DoesNotExist:
            pass

    # Shipping cost from request (frontend calculates based on governorate)
    shipping_cost = Decimal(str(request.data.get('shipping', 0)))
    tax_amount = Decimal('0')
    total = subtotal - discount_amount + shipping_cost + tax_amount

    # ── Create order ────────────────────────────────────────────────
    with transaction.atomic():
        order = Order.objects.create(
            user=user,  # None for guests
            subtotal=subtotal,
            shipping_cost=shipping_cost,
            discount_amount=discount_amount,
            tax_amount=tax_amount,
            total=total,
            coupon_code=coupon_code,
            payment_method=data.get('payment_method', 'cod'),
            customer_note=data.get('customer_note', ''),
            **shipping_data
        )

        # Create order items
        if use_backend_cart:
            for item in cart_items_data:
                # Safely get image URL — Django ImageField raises ValueError if no file is set
                try:
                    product_image_url = item.product.primary_image.url if item.product.primary_image and item.product.primary_image.name else ''
                except Exception:
                    product_image_url = ''

                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    variant=item.variant,
                    product_name=item.product.name,
                    product_image=product_image_url,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    line_total=item.line_total,
                    variant_details={'size': item.variant.size, 'color': item.variant.color} if item.variant else {}
                )
                # Stock reduction
                if item.variant:
                    ProductVariant.objects.filter(pk=item.variant.id).update(stock_quantity=F('stock_quantity') - item.quantity)
                else:
                    Product.objects.filter(pk=item.product.id, track_inventory=True).update(stock_quantity=F('stock_quantity') - item.quantity)
        else:
            # Guest cart items from request body
            for item in cart_items_data:
                price = Decimal(str(item.get('price', 0)))
                qty = int(item.get('quantity', 1))
                product_id = item.get('id')
                variant_id = item.get('variantId')
                
                OrderItem.objects.create(
                    order=order,
                    product_id=product_id,
                    variant_id=variant_id,
                    product_name=item.get('name', ''),
                    product_image=item.get('image', item.get('images', [''])[0] if item.get('images') else ''),
                    quantity=qty,
                    unit_price=price,
                    line_total=price * qty,
                    variant_details={
                        'size': item.get('size', ''),
                        'color': item.get('color', ''),
                    }
                )
                # Stock reduction
                if variant_id:
                    ProductVariant.objects.filter(pk=variant_id).update(stock_quantity=F('stock_quantity') - qty)
                elif product_id:
                    Product.objects.filter(pk=product_id, track_inventory=True).update(stock_quantity=F('stock_quantity') - qty)

        # Update coupon usage counter
        if coupon:
            coupon.used_count += 1
            coupon.save(update_fields=['used_count'])
            # Record per-user usage for authenticated users
            if user:
                from apps.coupons.models import CouponUsage
                CouponUsage.objects.create(coupon=coupon, user=user, order=order)

        # Clear backend cart for authenticated users
        if use_backend_cart:
            cart_items_data.delete() if hasattr(cart_items_data, 'delete') else None
            try:
                Cart.objects.get(user=user).items.all().delete()
            except Exception:
                pass

        # Status history
        OrderStatusHistory.objects.create(order=order, status='pending', note='Order placed.')

    # Send notification for logged-in users
    if user:
        try:
            from apps.notifications.models import Notification
            Notification.objects.create(
                user=user,
                type='order',
                title='Order Confirmed',
                message=f'Your order {order.order_number} has been placed. Total: {order.total} EGP.',
            )
        except Exception:
            pass

    return Response({
        'success': True,
        'message': 'Order placed successfully.',
        'order': OrderSerializer(order).data
    }, status=201)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def cancel_order(request, pk):
    try:
        order = Order.objects.get(pk=pk, user=request.user)
    except Order.DoesNotExist:
        return Response({'success': False, 'message': 'Order not found.'}, status=404)

    if order.status not in ['pending', 'confirmed']:
        return Response({'success': False, 'message': f'Cannot cancel order with status: {order.status}.'}, status=400)

    order.status = 'cancelled'
    order.save(update_fields=['status'])
    OrderStatusHistory.objects.create(order=order, status='cancelled', note='Cancelled by customer.')

    return Response({'success': True, 'message': 'Order cancelled.'})


# Admin views
class AdminOrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Order.objects.all().prefetch_related('items', 'status_history')


class AdminOrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Order.objects.all()


@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def update_order_status(request, pk):
    try:
        order = Order.objects.get(pk=pk)
    except Order.DoesNotExist:
        return Response({'success': False, 'message': 'Order not found.'}, status=404)

    serializer = UpdateOrderStatusSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    order.status = data['status']
    if data.get('tracking_number'):
        order.tracking_number = data['tracking_number']
    order.save()

    OrderStatusHistory.objects.create(
        order=order,
        status=data['status'],
        note=data.get('note', ''),
        changed_by=request.user
    )

    try:
        from apps.notifications.models import Notification
        Notification.objects.create(
            user=order.user,
            type='order',
            title=f'Order {data["status"].replace("_", " ").title()}',
            message=f'Your order {order.order_number} status updated to {data["status"]}.',
        )
    except Exception:
        pass

    return Response({'success': True, 'message': 'Order status updated.', 'order': OrderSerializer(order).data})