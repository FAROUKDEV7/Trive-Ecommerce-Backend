from django.urls import path
from . import views

urlpatterns = [
    path('', views.NotificationListView.as_view(), name='notifications'),
    path('mark-all-read/', views.mark_all_read, name='notifications-mark-all-read'),
    path('<int:pk>/read/', views.mark_read, name='notification-read'),
]