from django.urls import path
from . import views

app_name = 'materials'

urlpatterns = [
    path('' , views.dashboard, name='dashboard'),
    path('materials/', views.MaterialListView.as_view(), name='list'),
    path('materials/add/', views.MaterialCreateView.as_view(), name='add'),
    path('materials/<int:pk>/edit/', views.MaterialUpdateView.as_view(), name='edit'),
    path('materials/<int:pk>/delete/', views.MaterialDeleteView.as_view(), name='delete'),
    path('clients/', views.ClientListView.as_view(), name='client_list'),
    path('clients/add/', views.ClientCreateView.as_view(), name='client_add'),
    path('receptions/', views.ReceptionListView.as_view(), name='reception_list'),
    path('receptions/add/', views.comming_soon, name='comming_soon'),
    path('reception/new/', views.ReceptionCreateView.as_view(), name='reception_create'),
    path('reception/<int:pk>/edit/', views.ReceptionUpdateView.as_view(), name='reception_update'),
    path('reception/<int:pk>/delete/', views.ReceptionDeleteView.as_view(), name='reception_delete'),
    path('reception/<int:pk>/detail/', views.ReceptionDetailView.as_view(), name='reception_detail'),
    path('reception/complete/', views.ReceptionCompleteView.as_view(), name='reception_complete'),
]