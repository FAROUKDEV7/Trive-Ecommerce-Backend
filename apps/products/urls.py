from django.urls import path
from . import views

urlpatterns = [
    # Public
    path('', views.ProductListView.as_view(), name='product-list'),
    path('featured/', views.FeaturedProductsView.as_view(), name='featured-products'),
    path('new-arrivals/', views.NewArrivalsView.as_view(), name='new-arrivals'),
    path('sale/', views.SaleProductsView.as_view(), name='sale-products'),
    path('<slug:slug>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('<slug:slug>/related/', views.related_products, name='related-products'),

    # Admin
    path('admin/products/', views.AdminProductListCreateView.as_view(), name='admin-product-list'),
    path('admin/products/<uuid:pk>/', views.AdminProductDetailView.as_view(), name='admin-product-detail'),
    path('admin/products/<uuid:product_pk>/images/', views.ProductImageUploadView.as_view(), name='product-image-upload'),
    path('admin/images/<int:pk>/', views.delete_product_image, name='delete-product-image'),
]