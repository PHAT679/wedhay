from django.urls import path
from . import views

app_name = 'customer'

urlpatterns = [
    path('booking/', views.customer_booking_view, name='booking'),
    path('booking/<str:pk>/success/', views.customer_booking_success, name='booking_success'),
    path('my-appointments/', views.customer_my_appointments, name='my_appointments'),
    path('appointments/<str:pk>/reschedule/', views.customer_reschedule_view, name='reschedule'),
    path('appointments/<str:pk>/cancel/', views.customer_cancel_view, name='cancel'),
]
