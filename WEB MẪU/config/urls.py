from django.contrib import admin
from django.urls import path, include
from config.views import home_view
from apps.appointments.views import api_available_slots

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('accounts/', include('apps.accounts.urls')),
    path('services/', include('apps.services.urls')),
    path('customer/', include('apps.appointments.customer_urls')),
    path('owner/', include('apps.appointments.owner_urls')),
    path('employee/', include('apps.assignments.employee_urls')),
    path('payments/', include('apps.payments.urls')),
    path('notifications/', include('apps.notifications.urls')),
    path('api/slots/', api_available_slots, name='api_available_slots'),
]
