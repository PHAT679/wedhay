from django.urls import path
from . import views

app_name = 'employee'

urlpatterns = [
    path('', views.employee_dashboard, name='dashboard'),
    path('appointments/<str:pk>/', views.employee_appointment_detail, name='appointment_detail'),
    path('assignments/<str:pk>/accept/', views.employee_accept_assignment, name='accept_assignment'),
    path('assignments/<str:pk>/reject/', views.employee_reject_assignment, name='reject_assignment'),
]
