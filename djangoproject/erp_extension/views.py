from django.shortcuts import render
from django.contrib import messages
import MySQLdb
import sys

def view_clients(request):
    print("\n=== INICIANDO CONEXIÓN A MYSQL 2005 ===")
    messages.info(request, "Iniciando conexión con la base de datos ERP")

    try:
        print("Paso 1: Estableciendo conexión directa...")
        messages.info(request, "Conectando al servidor...")
        
        conn = MySQLdb.connect(
            host='26.110.109.182',
            user='root',
            passwd='',
            db='dpadmwin',
            charset='latin1',
            connect_timeout=10
        )
        print("✓ Conexión MySQL directa establecida")
        messages.success(request, "Conexión exitosa al servidor MySQL")

        cursor = conn.cursor()
        print("Paso 2: Cursor creado correctamente")

        # Consulta de prueba
        test_query = "SHOW TABLES"
        print(f"Paso 3: Ejecutando consulta de prueba: {test_query}")
        cursor.execute(test_query)
        print(f"✓ Tablas disponibles: {cursor.fetchall()}")
        messages.info(request, "Verificando estructura de la base de datos...")

        # Consulta real
        query = "SELECT * FROM dpclientes LIMIT 50"
        print(f"Paso 4: Ejecutando consulta principal: {query}")
        messages.info(request, "Obteniendo datos de clientes...")
        
        cursor.execute(query)
        columnas = [desc[0] for desc in cursor.description]
        datos = cursor.fetchall()
        
        print(f"✓ Datos obtenidos - Columnas: {columnas}")
        print(f"✓ Registros encontrados: {len(datos)}")
        messages.success(request, f"Datos cargados correctamente ({len(datos)} registros)")

        conn.close()
        print("Paso 5: Conexión cerrada")
        
        return render(request, 'erp_extension/ver_dpclientes.html', {
            'columnas': columnas,
            'datos': datos
        })
        
    except MySQLdb.Error as e:
        error_msg = f"Error MySQL ({e.args[0]}): {e.args[1]}"
        print(f"✗ ERROR: {error_msg}")
        print(f"Tipo de error: {sys.exc_info()[0]}")
        
        messages.error(request, "Error crítico al acceder a la base de datos")
        messages.warning(request, f"Detalle técnico: {e.args[1]} (Código: {e.args[0]})")

        return render(request, 'erp_extension/ver_dpclientes.html', {
            'columnas': [],
            'datos': []
        })
    
    finally:
        print("=== FIN DE EJECUCIÓN ===\n")