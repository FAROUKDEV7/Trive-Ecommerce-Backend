from django.contrib import admin
from .models import Order, OrderItem, OrderStatusHistory

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'variant', 'product_name', 'quantity', 'unit_price', 'line_total']

class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ['created_at']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'total', 'status', 'payment_status', 'created_at']
    list_filter = ['status', 'payment_status', 'created_at']
    search_fields = ['order_number', 'shipping_name', 'shipping_phone', 'user__email']
    readonly_fields = ['order_number', 'user', 'created_at', 'updated_at', 'total', 'subtotal', 'shipping_cost', 'discount_amount', 'tax_amount']
    inlines = [OrderItemInline, OrderStatusHistoryInline]
    
    fieldsets = (
        ('Order Info', {
            'fields': ('order_number', 'user', 'status', 'created_at', 'updated_at')
        }),
        ('Shipping Details', {
            'fields': (
                'shipping_name', 'shipping_phone', 'shipping_address_line1',
                'shipping_address_line2', 'shipping_city', 'shipping_state',
                'shipping_postal_code', 'shipping_country'
            )
        }),
        ('Payment & Totals', {
            'fields': ('payment_status', 'payment_method', 'subtotal', 'shipping_cost', 'discount_amount', 'tax_amount', 'total', 'coupon_code')
        }),
        ('Tracking & Notes', {
            'fields': ('tracking_number', 'estimated_delivery', 'customer_note', 'admin_note')
        }),
    )

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product_name', 'quantity', 'unit_price', 'line_total']
    list_filter = ['order__status', 'order__created_at']

@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['order', 'status', 'created_at', 'changed_by']
    list_filter = ['status', 'created_at']
