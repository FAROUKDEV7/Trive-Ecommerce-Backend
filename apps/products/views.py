from rest_framework import generics, filters, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from .models import Category, Product, ProductImage, ProductVariant
from .serializers import (
    CategorySerializer, ProductListSerializer, ProductDetailSerializer,
    ProductWriteSerializer, ProductImageSerializer, ProductVariantSerializer
)
from .filters import ProductFilter


class CategoryListView(generics.ListAPIView):
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        # Return only top-level categories; subcategories are nested
        return Category.objects.filter(is_active=True, parent__isnull=True)


class CategoryDetailView(generics.RetrieveAPIView):
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'
    queryset = Category.objects.filter(is_active=True)


class ProductListView(generics.ListAPIView):
    serializer_class = ProductListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'description', 'tags']
    ordering_fields = ['price', 'created_at', 'name']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = Product.objects.filter(status='active').select_related('category').prefetch_related('images', 'variants')
        return queryset


class ProductDetailView(generics.RetrieveAPIView):
    serializer_class = ProductDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'
    queryset = Product.objects.filter(status='active').select_related('category').prefetch_related('images', 'variants')


class FeaturedProductsView(generics.ListAPIView):
    serializer_class = ProductListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Product.objects.filter(status='active', is_featured=True).prefetch_related('images', 'variants')[:12]


class NewArrivalsView(generics.ListAPIView):
    serializer_class = ProductListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Product.objects.filter(status='active', is_new_arrival=True).prefetch_related('images', 'variants').order_by('-created_at')[:12]


class SaleProductsView(generics.ListAPIView):
    serializer_class = ProductListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Product.objects.filter(status='active', is_on_sale=True).prefetch_related('images', 'variants')


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def related_products(request, slug):
    try:
        product = Product.objects.get(slug=slug, status='active')
        qs = Product.objects.filter(
            status='active', category=product.category
        ).exclude(pk=product.pk).prefetch_related('images', 'variants')[:8]
        serializer = ProductListSerializer(qs, many=True, context={'request': request})
        return Response({'success': True, 'results': serializer.data})
    except Product.DoesNotExist:
        return Response({'success': False, 'message': 'Product not found.'}, status=404)


# --- Admin Views (staff only) ---

class AdminProductListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'sku']
    ordering_fields = ['price', 'created_at', 'stock_quantity']

    def get_queryset(self):
        return Product.objects.all().select_related('category')

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ProductListSerializer
        return ProductWriteSerializer


class AdminProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAdminUser]
    queryset = Product.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ProductDetailSerializer
        return ProductWriteSerializer

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)


class AdminCategoryListCreateView(generics.ListCreateAPIView):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Category.objects.all()


class AdminCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Category.objects.all()

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)


class ProductImageUploadView(generics.CreateAPIView):
    serializer_class = ProductImageSerializer
    permission_classes = [permissions.IsAdminUser]

    def perform_create(self, serializer):
        product = Product.objects.get(pk=self.kwargs['product_pk'])
        serializer.save(product=product)


@api_view(['DELETE'])
@permission_classes([permissions.IsAdminUser])
def delete_product_image(request, pk):
    try:
        image = ProductImage.objects.get(pk=pk)
        image.delete()
        return Response({'success': True, 'message': 'Image deleted.'})
    except ProductImage.DoesNotExist:
        return Response({'success': False, 'message': 'Image not found.'}, status=404)