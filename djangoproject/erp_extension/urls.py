from django.urls import path
from . import views

app_name = 'erp_extension'

urlpatterns = [
    path('', views.view_clients, name='view_clients'),
    ]

