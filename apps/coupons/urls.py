from django.urls import path
from . import views

urlpatterns = [
    path('validate/', views.validate_coupon, name='coupon-validate'),
    path('admin/', views.AdminCouponListCreateView.as_view(), name='admin-coupon-list'),
    path('admin/<int:pk>/', views.AdminCouponDetailView.as_view(), name='admin-coupon-detail'),
]