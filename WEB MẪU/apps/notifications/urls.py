from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.notifications_list_view, name='list'),
    path('<str:pk>/read/', views.notification_mark_read, name='mark_read'),
    path('mark-all-read/', views.mark_all_read, name='mark_all_read'),
]
