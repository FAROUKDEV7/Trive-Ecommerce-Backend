"""
TRIVE E-Commerce Backend - URL Configuration
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .analytics import dashboard_stats

# Customize admin
admin.site.site_header = 'TRIVÉ Admin'
admin.site.site_title = 'TRIVÉ Admin Portal'
admin.site.index_title = 'Welcome to TRIVÉ Administration'

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),

    # API v1
    path('api/v1/', include([
        path('auth/', include('apps.users.urls')),
        path('products/', include('apps.products.urls')),
        path('categories/', include('apps.products.category_urls')),
        path('cart/', include('apps.cart.urls')),
        path('wishlist/', include('apps.wishlist.urls')),
        path('orders/', include('apps.orders.urls')),
        path('coupons/', include('apps.coupons.urls')),
        path('reviews/', include('apps.reviews.urls')),
        path('payments/', include('apps.payments.urls')),
        path('notifications/', include('apps.notifications.urls')),
        path('contact/', include('apps.contact.urls')),
        path('admin/dashboard/', dashboard_stats, name='admin-dashboard'),
    ])),

    # Social Auth
    path('social-auth/', include('social_django.urls', namespace='social')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)