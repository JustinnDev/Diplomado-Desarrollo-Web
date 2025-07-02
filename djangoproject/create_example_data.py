#Este Script solo se puede ejecutar en python manage.py shell, si no nno funcionara. 
from materials.models import Client, MaterialType

def load_initial_data():
    # Datos de clientes
    clients_data = [
        {"name": "Jarlis Pérez", "identification": "V-12345678", "phone": "04141234567", "address": "Av. Principal, Caracas"},
        {"name": "María González", "identification": "V-87654321", "phone": "04241234567", "address": "Calle 5, Maracaibo"},
        {"name": "Carlos Rodríguez", "identification": "V-11223344", "phone": "04121234567", "address": "Urbanización Las Acacias, Valencia"},
        {"name": "Empresa ABC C.A.", "identification": "J-30123456", "phone": "04161234567", "address": "Zona Industrial, Barquisimeto"},
        {"name": "Luis Fernández", "identification": "V-55667788", "phone": "04131234567", "address": "Sector El Llano, Mérida"},
    ]

    # Datos de tipos de material
    materials_data = [
        {"name": "Hierro Corto", "category": "HIERRO", "base_price": 0.15},
        {"name": "Hierro Largo", "category": "HIERRO", "base_price": 0.18},
        {"name": "Acero Inoxidable", "category": "ACERO", "base_price": 0.35},
        {"name": "Aluminio Perfil", "category": "ALUMINIO", "base_price": 0.85},
        {"name": "Aluminio Calamina", "category": "ALUMINIO", "base_price": 0.75},
        {"name": "Cobre", "category": "COBRE", "base_price": 7.20},
        {"name": "Bronce", "category": "BRONCE", "base_price": 5.00},
    ]

    # Cargar clientes
    print("Cargando clientes...")
    for client_data in clients_data:
        client, created = Client.objects.get_or_create(
            identification=client_data["identification"],
            defaults={
                "name": client_data["name"],
                "phone": client_data["phone"],
                "address": client_data["address"]
            }
        )
        if created:
            print(f"Cliente creado: {client.name} ({client.identification})")
        else:
            print(f"Cliente ya existente: {client.name}")

    # Cargar materiales
    print("\nCargando materiales...")
    for material_data in materials_data:
        material, created = MaterialType.objects.get_or_create(
            name=material_data["name"],
            defaults={
                "category": material_data["category"],
                "base_price": material_data["base_price"]
            }
        )
        if created:
            print(f"Material creado: {material.name} ({material.get_category_display()}) - ${material.base_price}/kg")
        else:
            print(f"Material ya existente: {material.name}")

    print("\n¡Carga de datos completada!")

# Ejecutar la función
load_initial_data()