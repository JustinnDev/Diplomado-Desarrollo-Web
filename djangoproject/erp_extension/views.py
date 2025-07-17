from django.shortcuts import render
from django.contrib import messages
import pymysql 

def view_clients(request):
    print("\n=== CONEXIÓN MYSQL 2005 ===")
    messages.info(request, "Iniciando conexión con el ERP")

    try:
        conn = pymysql.connect(
            host='26.110.109.182',
            user='root',
            password='',
            database='dpadmwin',
            charset='latin1',
            connect_timeout=10
        )
        print("✓ Conexión via pymysql exitosa")

        cursor = conn.cursor()
        messages.success(request, "Conexión establecida")

        # Consulta compatible
        query = "SELECT * FROM dpclientes LIMIT 50"
        print(f"Ejecutando: {query}")
        cursor.execute(query)
        
        columnas = [desc[0] for desc in cursor.description]
        datos = cursor.fetchall()
        
        print(f"✓ Obtenidos {len(datos)} registros")
        messages.success(request, f"Datos cargados ({len(datos)} registros)")
        
        conn.close()
        return render(request, 'erp_extension/ver_dpclientes.html', {
            'columnas': columnas,
            'datos': datos
        })

    except Exception as e:
        error_type = type(e).__name__
        error_msg = str(e.args[1]) if len(e.args) > 1 else str(e)
        print(f"✗ ERROR ({error_type}): {error_msg}")
        
        messages.error(request, "Error al acceder al ERP")
        messages.warning(request, f"Detalle: {error_msg.split('(')[0]}")
        
        return render(request, 'erp_extension/ver_dpclientes.html', {
            'columnas': [],
            'datos': []
        })
    finally:
        print("=== FIN DE EJECUCIÓN ===")