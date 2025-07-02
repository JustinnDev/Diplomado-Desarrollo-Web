from django.contrib import admin
from .models import MaterialType, Client, MaterialReception, ReceptionMaterial, MaterialOperation

# Register your models here.

admin.site.register(MaterialType)
admin.site.register(Client)
admin.site.register(MaterialReception)          
admin.site.register(ReceptionMaterial)
admin.site.register(MaterialOperation)
