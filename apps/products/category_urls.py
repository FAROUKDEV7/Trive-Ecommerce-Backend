from django.urls import path
from .views import (
    CategoryListView, CategoryDetailView,
    AdminCategoryListCreateView, AdminCategoryDetailView
)

urlpatterns = [
    path('', CategoryListView.as_view(), name='category-list'),
    path('<slug:slug>/', CategoryDetailView.as_view(), name='category-detail'),
    path('admin/', AdminCategoryListCreateView.as_view(), name='admin-category-list'),
    path('admin/<int:pk>/', AdminCategoryDetailView.as_view(), name='admin-category-detail'),
]