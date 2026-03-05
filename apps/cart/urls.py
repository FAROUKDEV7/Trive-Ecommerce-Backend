from django.urls import path
from . import views

urlpatterns = [
    path('', views.CartView.as_view(), name='cart'),
    path('add/', views.add_to_cart, name='cart-add'),
    path('items/<int:item_id>/', views.update_cart_item, name='cart-item-update'),
    path('items/<int:item_id>/remove/', views.remove_cart_item, name='cart-item-remove'),
    path('clear/', views.clear_cart, name='cart-clear'),
]