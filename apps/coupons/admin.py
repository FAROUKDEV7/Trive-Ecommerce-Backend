from django.contrib import admin
from .models import Coupon, CouponUsage


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_type', 'discount_value', 'is_active', 'used_count', 'usage_limit', 'expires_at']
    list_filter = ['discount_type', 'is_active']
    search_fields = ['code', 'description']
    readonly_fields = ['used_count', 'created_at']


@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):
    list_display = ['coupon', 'user', 'order', 'used_at']
    list_filter = ['coupon']
    search_fields = ['coupon__code', 'user__email']