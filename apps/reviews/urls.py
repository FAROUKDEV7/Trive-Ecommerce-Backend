from django.urls import path
from . import views

urlpatterns = [
    path('products/<slug:slug>/', views.ProductReviewsView.as_view(), name='product-reviews'),
    path('create/', views.CreateReviewView.as_view(), name='create-review'),
    path('<int:pk>/helpful/', views.mark_helpful, name='review-helpful'),
    path('admin/all/', views.AdminReviewListView.as_view(), name='admin-reviews'),
    path('admin/<int:pk>/approve/', views.approve_review, name='admin-review-approve'),
]