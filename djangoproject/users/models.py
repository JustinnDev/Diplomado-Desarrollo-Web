from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Administrador'),
        ('staff', 'Personal'),
        ('licenciado', 'Licenciado'),
        ('obrero', 'Obrero'),
        ('visitante', 'Visitante'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='visitante')

    def is_admin(self):
        return self.role == 'admin'

    def is_staff_user(self):
        return self.role == 'staff'

    def __str__(self):
        return self.username