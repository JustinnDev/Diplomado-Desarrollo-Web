from django.db import models
from django.core.validators import MinValueValidator

class MaterialType(models.Model):
    CATEGORY_CHOICES = [
        ('HIERRO', 'Hierro'),
        ('ACERO', 'Acero'),
        ('ALUMINIO', 'Aluminio'),
        ('BRONCE', 'Bronce'),
        ('COBRE', 'Cobre'),
    ]
    
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    base_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    
    def __str__(self):
        return f"{self.name}"

class Client(models.Model):
    name = models.CharField(max_length=100)
    identification = models.CharField(max_length=20, unique=True)
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return self.name

class MaterialReception(models.Model):
    SUBTYPE_CHOICES = [
        ('CONTAMINADO', 'Contaminado'),
        ('LIMPIO', 'Limpio'),
        ('CON_PRODUCCION', 'Con producción'),
        ('SIN_PRODUCCION', 'Sin producción'),   
    ]
    
    DISCOUNT_TYPE_CHOICES = [
        ('NONE', 'Ninguno'),
        ('ABSOLUTE', 'Absoluto (kg)'),
        ('PERCENTAGE', 'Porcentaje'),
    ]
    
    client = models.ForeignKey(Client, on_delete=models.PROTECT)
    reception_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Recepción #{self.id} - {self.client.name}"

class ReceptionMaterial(models.Model):
    reception = models.ForeignKey(MaterialReception, on_delete=models.CASCADE, related_name='materials')
    material_type = models.ForeignKey(MaterialType, on_delete=models.PROTECT)
    subtype = models.CharField(max_length=20, choices=MaterialReception.SUBTYPE_CHOICES)
    discount_type = models.CharField(max_length=10, choices=MaterialReception.DISCOUNT_TYPE_CHOICES, default='NONE')
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    
    def calculate_net_weight(self):
        total = sum(op.net_weight for op in self.operations.all())
        if self.discount_type == 'PERCENTAGE':
            return total * (1 - self.discount_value/100)
        elif self.discount_type == 'ABSOLUTE':
            return total - self.discount_value
        return total
    
    def calculate_reception_total(self):
        return sum(material.total for material in self.reception.materials.all())

    @property
    def net_weight(self):
        return self.calculate_net_weight()
    
    @property
    def total(self):
        return self.net_weight * self.material_type.base_price

class MaterialOperation(models.Model):
    reception_material = models.ForeignKey(ReceptionMaterial, on_delete=models.CASCADE, related_name='operations')
    gross_weight = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    tare_weight = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    
    @property
    def net_weight(self):
        return self.gross_weight - self.tare_weight
    
    def __str__(self):
        return f"Op. {self.id}: {self.gross_weight}kg - {self.tare_weight}kg = {self.net_weight}kg"