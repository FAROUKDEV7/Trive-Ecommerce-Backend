from django.urls import path
from . import views

urlpatterns = [
    path('', views.WishlistView.as_view(), name='wishlist'),
    path('ids/', views.wishlist_ids, name='wishlist-ids'),
    path('toggle/<uuid:product_id>/', views.toggle_wishlist, name='wishlist-toggle'),
]