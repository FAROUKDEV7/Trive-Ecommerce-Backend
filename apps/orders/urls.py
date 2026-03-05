from django.urls import path
from . import views

urlpatterns = [
    path('', views.OrderListView.as_view(), name='order-list'),
    path('create/', views.create_order, name='order-create'),
    path('<uuid:pk>/', views.OrderDetailView.as_view(), name='order-detail'),
    path('<uuid:pk>/cancel/', views.cancel_order, name='order-cancel'),
    # Admin
    path('admin/all/', views.AdminOrderListView.as_view(), name='admin-order-list'),
    path('admin/<uuid:pk>/', views.AdminOrderDetailView.as_view(), name='admin-order-detail'),
    path('admin/<uuid:pk>/status/', views.update_order_status, name='admin-order-status'),
]