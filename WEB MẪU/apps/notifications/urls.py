from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.notifications_list_view, name='list'),
    path('owner-status/', views.owner_notification_status, name='owner_status'),
    path('<str:pk>/read/', views.notification_mark_read, name='mark_read'),
    path('mark-all-read/', views.mark_all_read, name='mark_all_read'),
]
