from django.contrib import admin
from .models import Driver, Vehicle, FuelStation, FuelRefill, FuelConsumption, MaintenanceLog

@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ('name', 'license_number', 'license_type', 'is_active')
    search_fields = ('name', 'license_number')
    list_filter = ('is_active', 'license_type')

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('license_plate', 'make', 'model', 'vehicle_type', 'fuel_type', 'current_driver', 'is_active')
    search_fields = ('license_plate', 'make', 'model')
    list_filter = ('is_active', 'vehicle_type', 'fuel_type')
    raw_id_fields = ('current_driver',)

@admin.register(FuelStation)
class FuelStationAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'is_active')
    search_fields = ('name', 'location')
    list_filter = ('is_active',)

@admin.register(FuelRefill)
class FuelRefillAdmin(admin.ModelAdmin):
    list_display = ('date', 'vehicle', 'driver', 'station', 'quantity', 'price_per_unit', 'total_cost')
    search_fields = ('vehicle__license_plate', 'driver__name')
    list_filter = ('station', 'date')
    raw_id_fields = ('vehicle', 'driver', 'station')
    date_hierarchy = 'date'

@admin.register(FuelConsumption)
class FuelConsumptionAdmin(admin.ModelAdmin):
    list_display = ('date', 'vehicle', 'driver', 'quantity', 'odometer_reading', 'km_since_last', 'efficiency')
    search_fields = ('vehicle__license_plate', 'driver__name')
    raw_id_fields = ('vehicle', 'driver')
    date_hierarchy = 'date'

@admin.register(MaintenanceLog)
class MaintenanceLogAdmin(admin.ModelAdmin):
    list_display = ('date', 'vehicle', 'maintenance_type', 'cost', 'odometer_reading')
    search_fields = ('vehicle__license_plate', 'description')
    list_filter = ('maintenance_type', 'date')
    raw_id_fields = ('vehicle',)
    date_hierarchy = 'date'