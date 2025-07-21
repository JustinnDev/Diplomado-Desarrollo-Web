from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone

class Driver(models.Model):
    """Modelo para conductores de la empresa"""
    name = models.CharField(max_length=100)
    license_number = models.CharField(max_length=20, unique=True)
    license_type = models.CharField(max_length=50)
    phone = models.CharField(max_length=15, blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

class Vehicle(models.Model):
    """Modelo para los vehículos de la empresa"""
    VEHICLE_TYPE_CHOICES = [
        ('TRUCK', 'Camión'),
        ('FORKLIFT', 'Montacargas'),
        ('VAN', 'Camioneta'),
        ('OTHER', 'Otro'),
    ]
    
    FUEL_TYPE_CHOICES = [
        ('GASOLINE', 'Gasolina'),
        ('DIESEL', 'Diésel'),
        ('GAS', 'Gas'),
        ('HYBRID', 'Híbrido'),
    ]
    
    license_plate = models.CharField(max_length=20, unique=True)
    make = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    year = models.PositiveIntegerField()
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPE_CHOICES)
    fuel_type = models.CharField(max_length=20, choices=FUEL_TYPE_CHOICES)
    fuel_capacity = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        validators=[MinValueValidator(0)],
        help_text="Capacidad del tanque en litros"
    )
    current_driver = models.ForeignKey(
        Driver, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='assigned_vehicle'
    )
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.get_vehicle_type_display()} {self.make} {self.model} ({self.license_plate})"
    
    @property
    def current_fuel_level(self):
        """Calcula el nivel actual de combustible basado en las recargas"""
        from django.db.models import Sum
        total_refueled = FuelRefill.objects.filter(
            vehicle=self
        ).aggregate(
            total=Sum('quantity')
        )['total'] or 0
        
        total_consumed = FuelConsumption.objects.filter(
            vehicle=self
        ).aggregate(
            total=Sum('quantity')
        )['total'] or 0
        
        return total_refueled - total_consumed

class FuelStation(models.Model):
    """Modelo para estaciones de servicio/combustible"""
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    contact_phone = models.CharField(max_length=15, blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

class FuelRefill(models.Model):
    """Modelo para registrar recargas de combustible"""
    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT, related_name='refills')
    driver = models.ForeignKey(Driver, on_delete=models.PROTECT, related_name='fuel_refills')
    station = models.ForeignKey(FuelStation, on_delete=models.PROTECT, related_name='refills')
    date = models.DateTimeField(auto_now_add=False)
    quantity = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        validators=[MinValueValidator(0.01)],
        help_text="Cantidad en litros"
    )
    price_per_unit = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        validators=[MinValueValidator(0)],
        help_text="Precio por litro"
    )
    odometer_reading = models.PositiveIntegerField(
        help_text="Lectura del odómetro al momento de la recarga"
    )
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"Recarga {self.id} - {self.vehicle.license_plate}"
    
    @property
    def total_cost(self):
        return self.quantity * self.price_per_unit
    


class FuelConsumption(models.Model):
    """Modelo para registrar consumo de combustible"""
    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT, related_name='consumptions')
    driver = models.ForeignKey(Driver, on_delete=models.PROTECT, related_name='fuel_consumptions')
    date = models.DateTimeField(default=timezone.now)
    quantity = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        validators=[MinValueValidator(0.01)],
        help_text="Cantidad en litros"
    )
    odometer_reading = models.PositiveIntegerField(
        help_text="Lectura del odómetro al momento del registro"
    )
    purpose = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"Consumo {self.id} - {self.vehicle.license_plate}"
    
    @property
    def km_since_last(self):
        """Calcula los kilómetros recorridos desde el último registro"""
        last_record = FuelConsumption.objects.filter(
            vehicle=self.vehicle
        ).exclude(
            id=self.id
        ).order_by('-date').first()
        
        if last_record:
            return self.odometer_reading - last_record.odometer_reading
        return 0
    
    @property
    def efficiency(self):
        """Calcula la eficiencia en km/litro (si hay km recorridos)"""
        km = self.km_since_last
        if km > 0 and self.quantity > 0: 
            return km / float(self.quantity)
        
        return 0

class MaintenanceLog(models.Model):
    """Modelo para registrar mantenimientos de vehículos"""
    MAINTENANCE_TYPE_CHOICES = [
        ('PREVENTIVE', 'Preventivo'),
        ('CORRECTIVE', 'Correctivo'),
        ('OTHER', 'Otro'),
    ]
    
    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT, related_name='maintenances')
    date = models.DateTimeField(auto_now_add=True)
    maintenance_type = models.CharField(max_length=20, choices=MAINTENANCE_TYPE_CHOICES)
    description = models.TextField()
    cost = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0)],
        default=0
    )
    odometer_reading = models.PositiveIntegerField()
    next_maintenance_km = models.PositiveIntegerField(
        null=True, 
        blank=True,
        help_text="Próximo mantenimiento en X kilómetros"
    )
    performed_by = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"Mantenimiento {self.id} - {self.vehicle.license_plate}"