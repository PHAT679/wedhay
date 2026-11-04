from django.urls import path
from apps.appointments import views as appointment_views
from apps.services import views as service_views
from apps.accounts import views as account_views
from apps.assignments import views as assignment_views

app_name = 'owner'

urlpatterns = [
    # Dashboard & Timeline
    path('', appointment_views.owner_dashboard, name='dashboard'),
    path('timeline/', appointment_views.owner_timeline_view, name='timeline'),
    
    # Quản lý Lịch hẹn (UC3)
    path('appointments/', appointment_views.owner_appointments_list, name='appointments_list'),
    path('appointments/<str:pk>/', appointment_views.owner_appointment_detail, name='appointment_detail'),
    path('appointments/<str:pk>/status/', appointment_views.owner_update_status, name='appointment_update_status'),

    # Quản lý Dịch vụ (UC4)
    path('services/', service_views.owner_services_list, name='services_list'),
    path('services/create/', service_views.owner_service_create, name='service_create'),
    path('services/<str:pk>/edit/', service_views.owner_service_update, name='service_update'),
    path('services/<str:pk>/delete/', service_views.owner_service_delete, name='service_delete'),

    # Quản lý Khách hàng (UC6)
    path('customers/', account_views.owner_customers_list, name='customers_list'),
    path('customers/create/', account_views.owner_customer_create, name='customer_create'),
    path('customers/<str:pk>/', account_views.owner_customer_detail, name='customer_detail'),
    path('customers/<str:pk>/edit/', account_views.owner_customer_update, name='customer_update'),

    # Quản lý Phân công Nhân viên (UC5)
    path('assignments/', assignment_views.owner_assignments_list, name='assignments_list'),
    path('assignments/assign/<str:appointment_pk>/', assignment_views.owner_assign_staff, name='assign_staff'),
]
