from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer, AddToCartSerializer, UpdateCartItemSerializer
from apps.products.models import Product, ProductVariant


def get_or_create_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart


class CartView(generics.RetrieveAPIView):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return get_or_create_cart(self.request.user)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def add_to_cart(request):
    serializer = AddToCartSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    try:
        product = Product.objects.get(pk=data['product_id'], status='active')
    except Product.DoesNotExist:
        return Response({'success': False, 'message': 'Product not found.'}, status=404)

    variant = None
    if data.get('variant_id'):
        try:
            variant = ProductVariant.objects.get(pk=data['variant_id'], product=product)
        except ProductVariant.DoesNotExist:
            return Response({'success': False, 'message': 'Variant not found.'}, status=404)

    cart = get_or_create_cart(request.user)
    item, created = CartItem.objects.get_or_create(
        cart=cart, product=product, variant=variant,
        defaults={'quantity': data['quantity']}
    )
    if not created:
        item.quantity += data['quantity']
        item.save()

    cart_serializer = CartSerializer(cart, context={'request': request})
    return Response({
        'success': True,
        'message': 'Item added to cart.',
        'cart': cart_serializer.data
    }, status=201 if created else 200)


@api_view(['PATCH'])
@permission_classes([permissions.IsAuthenticated])
def update_cart_item(request, item_id):
    serializer = UpdateCartItemSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    quantity = serializer.validated_data['quantity']

    try:
        cart = get_or_create_cart(request.user)
        item = CartItem.objects.get(pk=item_id, cart=cart)
    except CartItem.DoesNotExist:
        return Response({'success': False, 'message': 'Cart item not found.'}, status=404)

    if quantity == 0:
        item.delete()
        message = 'Item removed from cart.'
    else:
        item.quantity = quantity
        item.save()
        message = 'Cart updated.'

    cart_serializer = CartSerializer(cart, context={'request': request})
    return Response({'success': True, 'message': message, 'cart': cart_serializer.data})


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def remove_cart_item(request, item_id):
    try:
        cart = get_or_create_cart(request.user)
        item = CartItem.objects.get(pk=item_id, cart=cart)
        item.delete()
        cart_serializer = CartSerializer(cart, context={'request': request})
        return Response({'success': True, 'message': 'Item removed from cart.', 'cart': cart_serializer.data})
    except CartItem.DoesNotExist:
        return Response({'success': False, 'message': 'Cart item not found.'}, status=404)


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def clear_cart(request):
    cart = get_or_create_cart(request.user)
    cart.items.all().delete()
    return Response({'success': True, 'message': 'Cart cleared.'})
