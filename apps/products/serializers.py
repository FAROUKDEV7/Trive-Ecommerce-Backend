from rest_framework import serializers
from .models import Category, Product, ProductImage, ProductVariant


class CategorySerializer(serializers.ModelSerializer):
    subcategories = serializers.SerializerMethodField()
    product_count = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'image', 'image_url', 'parent', 'subcategories', 'product_count', 'sort_order']

    def get_subcategories(self, obj):
        if obj.subcategories.exists():
            return CategorySerializer(obj.subcategories.filter(is_active=True), many=True, context=self.context).data
        return []

    def get_product_count(self, obj):
        return obj.products.filter(status='active').count()

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None


class ProductImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'image_url', 'alt_text', 'is_primary', 'sort_order']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None


class ProductVariantSerializer(serializers.ModelSerializer):
    effective_price = serializers.ReadOnlyField()
    is_in_stock = serializers.ReadOnlyField()

    class Meta:
        model = ProductVariant
        fields = ['id', 'size', 'color', 'color_hex', 'sku', 'price', 'effective_price', 'stock_quantity', 'is_in_stock', 'is_active']


class ProductListSerializer(serializers.ModelSerializer):
    primary_image = serializers.SerializerMethodField()
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_slug = serializers.CharField(source='category.slug', read_only=True)
    discount_percentage = serializers.ReadOnlyField()
    is_in_stock = serializers.ReadOnlyField()
    average_rating = serializers.ReadOnlyField()
    review_count = serializers.ReadOnlyField()
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'short_description', 'category', 'category_name', 'category_slug',
            'price', 'compare_at_price', 'discount_percentage', 'stock_quantity',
            'is_in_stock', 'is_featured', 'is_new_arrival', 'is_on_sale',
            'primary_image', 'images', 'variants', 'average_rating', 'review_count', 'created_at'
        ]

    def get_primary_image(self, obj):
        request = self.context.get('request')
        image = obj.images.filter(is_primary=True).first() or obj.images.first()
        if image and request:
            return request.build_absolute_uri(image.image.url)
        return None


class ProductDetailSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    discount_percentage = serializers.ReadOnlyField()
    is_in_stock = serializers.ReadOnlyField()
    average_rating = serializers.ReadOnlyField()
    review_count = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'short_description',
            'category', 'price', 'compare_at_price', 'discount_percentage',
            'sku', 'track_inventory', 'stock_quantity', 'is_in_stock',
            'status', 'is_featured', 'is_new_arrival', 'is_on_sale',
            'weight', 'material', 'care_instructions', 'tags',
            'images', 'variants', 'average_rating', 'review_count',
            'meta_title', 'meta_description', 'created_at', 'updated_at'
        ]


class ProductWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        exclude = ['id', 'created_at', 'updated_at']