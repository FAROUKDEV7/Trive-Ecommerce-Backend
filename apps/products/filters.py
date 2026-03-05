import django_filters
from .models import Product


class ProductFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    category = django_filters.CharFilter(field_name='category__slug')
    is_featured = django_filters.BooleanFilter()
    is_new_arrival = django_filters.BooleanFilter()
    is_on_sale = django_filters.BooleanFilter()
    in_stock = django_filters.BooleanFilter(method='filter_in_stock')
    size = django_filters.CharFilter(method='filter_by_size')
    color = django_filters.CharFilter(method='filter_by_color')

    class Meta:
        model = Product
        fields = ['category', 'min_price', 'max_price', 'is_featured', 'is_new_arrival', 'is_on_sale']

    def filter_in_stock(self, queryset, name, value):
        if value:
            return queryset.filter(stock_quantity__gt=0)
        return queryset

    def filter_by_size(self, queryset, name, value):
        return queryset.filter(variants__size__iexact=value).distinct()

    def filter_by_color(self, queryset, name, value):
        return queryset.filter(variants__color__iexact=value).distinct()