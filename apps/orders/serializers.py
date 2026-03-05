from rest_framework import serializers
from .models import Order, OrderItem, OrderStatusHistory
from apps.users.models import Address


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'variant', 'product_name', 'product_image', 'variant_details', 'quantity', 'unit_price', 'line_total']


class OrderStatusHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatusHistory
        fields = ['id', 'status', 'note', 'created_at']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status_history = OrderStatusHistorySerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ['id', 'order_number', 'user', 'created_at', 'updated_at']


class OrderListSerializer(serializers.ModelSerializer):
    item_count = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'order_number', 'status', 'payment_status', 'total', 'item_count', 'created_at']

    def get_item_count(self, obj):
        return obj.items.count()


class CreateOrderSerializer(serializers.Serializer):
    address_id = serializers.IntegerField(required=False)
    shipping_name = serializers.CharField(required=False)
    shipping_phone = serializers.CharField(required=False)
    shipping_address_line1 = serializers.CharField(required=False)
    shipping_address_line2 = serializers.CharField(required=False, allow_blank=True)
    shipping_city = serializers.CharField(required=False)
    shipping_state = serializers.CharField(required=False)
    shipping_postal_code = serializers.CharField(required=False)
    shipping_country = serializers.CharField(required=False, default='Egypt')
    coupon_code = serializers.CharField(required=False, allow_blank=True)
    customer_note = serializers.CharField(required=False, allow_blank=True)
    payment_method = serializers.CharField(default='cod')


class UpdateOrderStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Order.STATUS_CHOICES)
    note = serializers.CharField(required=False, allow_blank=True)
    tracking_number = serializers.CharField(required=False, allow_blank=True)