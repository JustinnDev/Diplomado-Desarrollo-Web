from django.urls import path
from . import views

app_name = 'erp_extension'

urlpatterns = [
    path('' , views.view_clients, name='view_clients'),
    path('trello/', views.TrelloExplorerView.as_view(), name='crm'),
    path('trello/', views.TrelloExplorerView.as_view(), name='trello_explorer'),
    path('trello/workspaces/', views.TrelloExplorerView.as_view(), name='trello_workspaces'),
    path('trello/workspaces/<str:workspace_id>/', views.TrelloExplorerView.as_view(), name='workspace_boards'),
    path('trello/boards/<str:board_id>/', views.TrelloExplorerView.as_view(), name='board_detail'),
        # URLs para Dashboard de Combustible
    path('fuel/', views.FuelDashboardView.as_view(), name='fuel_dashboard'),
    
    # URLs para Conductores
    path('drivers/', views.DriverListView.as_view(), name='driver_list'),
    path('drivers/add/', views.DriverCreateView.as_view(), name='driver_create'),
    path('drivers/<int:pk>/edit/', views.DriverUpdateView.as_view(), name='driver_update'),
    
    # URLs para Vehículos
    path('vehicles/', views.VehicleListView.as_view(), name='vehicle_list'),
    path('vehicles/add/', views.VehicleCreateView.as_view(), name='vehicle_create'),
    path('vehicles/<int:pk>/edit/', views.VehicleUpdateView.as_view(), name='vehicle_update'),
    path('vehicles/<int:pk>/', views.VehicleDetailView.as_view(), name='vehicle_detail'),
    
    # URLs para Estaciones de Combustible
    path('fuel-stations/', views.FuelStationListView.as_view(), name='fuelstation_list'),
    path('fuel-stations/add/', views.FuelStationCreateView.as_view(), name='fuelstation_create'),
    
    # URLs para Recargas de Combustible
    path('fuel-refills/', views.FuelRefillListView.as_view(), name='fuelrefill_list'),
    path('fuel-refills/add/', views.FuelRefillCreateView.as_view(), name='fuelrefill_create'),
    path('vehicles/<int:vehicle_id>/fuel-refills/add/', views.FuelRefillCreateView.as_view(), name='vehicle_fuelrefill_create'),
    
    path('fuel-consumptions/add/', views.FuelConsumptionCreateView.as_view(), name='fuelconsumption_create'),
    path('vehicles/<int:vehicle_id>/fuel-consumptions/add/', views.FuelConsumptionCreateView.as_view(), name='vehicle_fuelconsumption_create'),
    path('fuel-consumptions/<int:pk>/edit/', views.FuelConsumptionUpdateView.as_view(), name='fuelconsumption_update'),
    path('vehicles/<int:vehicle_id>/fuel-consumptions/<int:pk>/edit/', views.FuelConsumptionUpdateView.as_view(), name='vehicle_fuelconsumption_update'),
    
    # URLs para Mantenimientos
    path('maintenances/', views.MaintenanceLogListView.as_view(), name='maintenance_list'),
    path('maintenances/add/', views.MaintenanceLogCreateView.as_view(), name='maintenance_create'),
    path('vehicles/<int:vehicle_id>/maintenances/add/', views.MaintenanceLogCreateView.as_view(), name='vehicle_maintenance_create'),

         
    # Añade estas URLs junto con las demás de mantenimiento
    path('maintenances/<int:pk>/', views.MaintenanceLogDetailView.as_view(), name='maintenance_detail'),
    path('maintenances/<int:pk>/edit/', views.MaintenanceLogUpdateView.as_view(), name='maintenance_update'),

    path('fuel-refills/<int:pk>/edit/', views.FuelRefillUpdateView.as_view(), name='fuelrefill_update'),
    path('vehicles/<int:vehicle_id>/fuel-refills/<int:pk>/edit/',views.FuelRefillUpdateView.as_view(), name='vehicle_fuelrefill_update'),
    ]


