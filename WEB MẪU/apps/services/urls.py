from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    path('', views.public_services_list, name='public_list'),
]
