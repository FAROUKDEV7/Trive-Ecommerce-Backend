from django.contrib import admin
from .models import Category, Product, ProductImage, ProductVariant


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'is_active', 'sort_order']
    list_filter = ['is_active', 'parent']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock_quantity', 'status', 'is_featured', 'is_on_sale']
    list_filter = ['status', 'is_featured', 'is_new_arrival', 'is_on_sale', 'category']
    search_fields = ['name', 'sku']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ProductVariantInline]
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Basic Info', {'fields': ('name', 'slug', 'description', 'short_description', 'category')}),
        ('Pricing', {'fields': ('price', 'compare_at_price', 'cost_per_item')}),
        ('Inventory', {'fields': ('sku', 'barcode', 'track_inventory', 'stock_quantity', 'low_stock_threshold')}),
        ('Status', {'fields': ('status', 'is_featured', 'is_new_arrival', 'is_on_sale')}),
        ('Details', {'fields': ('weight', 'material', 'care_instructions', 'tags')}),
        ('SEO', {'fields': ('meta_title', 'meta_description')}),
        ('Dates', {'fields': ('created_at', 'updated_at')}),
    )