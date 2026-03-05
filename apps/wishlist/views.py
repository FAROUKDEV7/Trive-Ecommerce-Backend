from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .models import WishlistItem
from .serializers import WishlistItemSerializer
from apps.products.models import Product


class WishlistView(generics.ListAPIView):
    serializer_class = WishlistItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return WishlistItem.objects.filter(user=self.request.user).select_related('product')


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def toggle_wishlist(request, product_id):
    try:
        product = Product.objects.get(pk=product_id, status='active')
    except Product.DoesNotExist:
        return Response({'success': False, 'message': 'Product not found.'}, status=404)

    item, created = WishlistItem.objects.get_or_create(user=request.user, product=product)
    if not created:
        item.delete()
        return Response({'success': True, 'message': 'Removed from wishlist.', 'in_wishlist': False})
    return Response({'success': True, 'message': 'Added to wishlist.', 'in_wishlist': True}, status=201)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def wishlist_ids(request):
    ids = list(WishlistItem.objects.filter(user=request.user).values_list('product_id', flat=True))
    return Response({'success': True, 'product_ids': [str(i) for i in ids]})