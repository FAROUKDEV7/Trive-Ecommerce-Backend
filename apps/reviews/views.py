from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .models import Review
from .serializers import ReviewSerializer, CreateReviewSerializer
from apps.products.models import Product


class ProductReviewsView(generics.ListAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Review.objects.filter(
            product__slug=self.kwargs['slug'], is_approved=True
        ).select_related('user')


class CreateReviewView(generics.CreateAPIView):
    serializer_class = CreateReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        product = serializer.validated_data['product']
        # Check verified purchase
        from apps.orders.models import Order
        is_verified = Order.objects.filter(
            user=self.request.user, items__product=product, status='delivered'
        ).exists()
        serializer.save(user=self.request.user, is_verified_purchase=is_verified)

    def create(self, request, *args, **kwargs):
        if Review.objects.filter(user=request.user, product=request.data.get('product')).exists():
            return Response({'success': False, 'message': 'You have already reviewed this product.'}, status=400)
        return super().create(request, *args, **kwargs)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_helpful(request, pk):
    try:
        review = Review.objects.get(pk=pk, is_approved=True)
        review.helpful_count += 1
        review.save(update_fields=['helpful_count'])
        return Response({'success': True, 'helpful_count': review.helpful_count})
    except Review.DoesNotExist:
        return Response({'success': False, 'message': 'Review not found.'}, status=404)


# Admin
class AdminReviewListView(generics.ListAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Review.objects.all().select_related('user', 'product')


@api_view(['PATCH'])
@permission_classes([permissions.IsAdminUser])
def approve_review(request, pk):
    try:
        review = Review.objects.get(pk=pk)
        review.is_approved = not review.is_approved
        review.save(update_fields=['is_approved'])
        return Response({'success': True, 'is_approved': review.is_approved})
    except Review.DoesNotExist:
        return Response({'success': False, 'message': 'Review not found.'}, status=404)