from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import permissions
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from datetime import timedelta

from apps.orders.models import Order
from apps.products.models import Product
from apps.users.models import User
from apps.reviews.models import Review


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def dashboard_stats(request):
    now = timezone.now()
    thirty_days_ago = now - timedelta(days=30)
    seven_days_ago = now - timedelta(days=7)

    # Orders
    total_orders = Order.objects.count()
    orders_this_month = Order.objects.filter(created_at__gte=thirty_days_ago).count()
    revenue_total = Order.objects.filter(payment_status='paid').aggregate(Sum('total'))['total__sum'] or 0
    revenue_this_month = Order.objects.filter(
        payment_status='paid', created_at__gte=thirty_days_ago
    ).aggregate(Sum('total'))['total__sum'] or 0

    # Orders by status
    orders_by_status = dict(
        Order.objects.values('status').annotate(count=Count('id')).values_list('status', 'count')
    )

    # Products
    total_products = Product.objects.filter(status='active').count()
    low_stock = Product.objects.filter(track_inventory=True, stock_quantity__lte=5, stock_quantity__gt=0).count()
    out_of_stock = Product.objects.filter(track_inventory=True, stock_quantity=0).count()

    # Users
    total_users = User.objects.count()
    new_users_this_month = User.objects.filter(date_joined__gte=thirty_days_ago).count()

    # Recent orders
    recent_orders = Order.objects.order_by('-created_at')[:5].values(
        'order_number', 'status', 'total', 'created_at'
    )

    # Revenue last 7 days (daily)
    daily_revenue = []
    for i in range(7):
        day = now - timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day.replace(hour=23, minute=59, second=59)
        rev = Order.objects.filter(
            payment_status='paid',
            created_at__range=[day_start, day_end]
        ).aggregate(Sum('total'))['total__sum'] or 0
        daily_revenue.append({'date': day.date().isoformat(), 'revenue': float(rev)})

    return Response({
        'success': True,
        'stats': {
            'orders': {
                'total': total_orders,
                'this_month': orders_this_month,
                'by_status': orders_by_status,
            },
            'revenue': {
                'total': float(revenue_total),
                'this_month': float(revenue_this_month),
                'daily_last_7_days': list(reversed(daily_revenue)),
            },
            'products': {
                'total_active': total_products,
                'low_stock': low_stock,
                'out_of_stock': out_of_stock,
            },
            'users': {
                'total': total_users,
                'new_this_month': new_users_this_month,
            },
        },
        'recent_orders': list(recent_orders),
    })