from django.db import models
from django.core.validators import MinValueValidator

class Material(models.Model):
    CATEGORY_CHOICES = [
        ('HIERRO', 'Hierro'),
        ('ACERO', 'Acero'),
        ('ALUMINIO', 'Aluminio'),
        ('BRONCE', 'Bronce'),
        ('COBRE', 'Cobre'),

    ]
    
    
    SUBTYPE_CHOICES = [
        ('CONTAMINADO', 'Contaminado'),
        ('LIMPIO', 'Limpio'),
        ('CON_PRODUCCION', 'Con producción'),
        ('SIN_PRODUCCION', 'Sin producción'),
       
    ]
    
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    subtype = models.CharField(max_length=20, choices=SUBTYPE_CHOICES)
    base_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_category_display()} - {self.get_subtype_display()}"

class Client(models.Model):
    name = models.CharField(max_length=100)
    identification = models.CharField(max_length=20, unique=True)
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return self.name

class MaterialReception(models.Model):
    client = models.ForeignKey(Client, on_delete=models.PROTECT)
    material = models.ForeignKey(Material, on_delete=models.PROTECT)
    gross_weight = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    rejection_weight = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    net_weight = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    total = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    reception_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def save(self, *args, **kwargs):
     
        if not self.net_weight:
            self.net_weight = self.gross_weight - self.rejection_weight
      
        if not self.total:
            self.total = self.net_weight * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Recepción #{self.id} - {self.client.name}"