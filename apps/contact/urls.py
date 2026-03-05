from django.urls import path
from . import views

urlpatterns = [
    path('', views.ContactCreateView.as_view(), name='contact'),
    path('admin/', views.AdminContactListView.as_view(), name='admin-contact-list'),
]