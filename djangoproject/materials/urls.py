from django.urls import path
from . import views

app_name = 'materials'

urlpatterns = [
    path('' , views.dashboard, name='dashboard'),
    path('materials/', views.MaterialListView.as_view(), name='list'),
    path('materials/add/', views.MaterialCreateView.as_view(), name='add'),
    path('materials/add_db/', views.add_material, name='add_db'),
    path('materials/<int:pk>/edit/', views.MaterialUpdateView.as_view(), name='edit'),
    path('materials/<int:pk>/edit_db/', views.edit_material, name='edit_db'),
    path('materials/<int:pk>/delete/', views.MaterialDeleteView.as_view(), name='delete'),
    path('materials/<int:pk>/delete_db/', views.delete_material, name='delete_db'),
    path('clients/', views.ClientListView.as_view(), name='client_list'),
    path('clients/add/', views.ClientCreateView.as_view(), name='client_add'),
    path('receptions/', views.ReceptionListView.as_view(), name='reception_list'),
    path('receptions/add/', views.reception_create, name='reception_add'),
    path('receptions/<int:pk>/', views.reception_detail, name='reception_detail'),
]