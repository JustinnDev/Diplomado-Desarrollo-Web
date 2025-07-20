from django.shortcuts import render
from django.contrib import messages
import pymysql 
from django.http import JsonResponse
from django.views import View
from .trello_utils import verify_trello_connection, get_all_workspaces, get_boards_by_workspace, get_board_details, create_list, create_card
from django.views.generic import ListView, CreateView
from django.urls import reverse_lazy
from trello import TrelloClient
from django.conf import settings
from django.views.generic import TemplateView

class TrelloConnectionTestView(View):
    def get(self, request):
        """
        Vista para probar la conexión con Trello y mostrar resultados en HTML
        """
        test_result = verify_trello_connection()
        
        context = {
            'test_result': test_result,
            'page_title': 'Prueba de conexión con Trello'
        }
        
        return render(request, 'erp_extension/crm.html', context)

class TrelloExplorerView(TemplateView):
    template_name = 'erp_extension/crm.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        workspace_id = self.kwargs.get('workspace_id')
        board_id = self.kwargs.get('board_id')
        
        try:
            if board_id:
                # Vista de detalle de tablero
                context['board'] = get_board_details(board_id)
                context['view_type'] = 'board_detail'
            elif workspace_id:
                # Vista de tableros del workspace
                context['boards'] = get_boards_by_workspace(workspace_id)
                context['current_workspace_id'] = workspace_id
                context['view_type'] = 'workspace_boards'
            else:
                # Vista principal de workspaces
                context['workspaces'] = get_all_workspaces()
                context['view_type'] = 'workspaces'
                
        except Exception as e:
            context['error'] = str(e)
            
        return context
    
    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')
        board_id = kwargs.get('board_id')
        
        try:
            if action == 'create_list':
                list_name = request.POST.get('list_name')
                new_list = create_list(board_id, list_name)
                return JsonResponse({
                    'success': True,
                    'list': {
                        'id': new_list.id,
                        'name': new_list.name
                    }
                })
                
            elif action == 'create_card':
                list_id = request.POST.get('list_id')
                card_name = request.POST.get('card_name')
                card_desc = request.POST.get('card_desc', '')
                due_date = request.POST.get('due_date')
                
                new_card = create_card(
                    list_id, 
                    card_name, 
                    card_desc, 
                    due_date if due_date else None
                )
                
                return JsonResponse({
                    'success': True,
                    'card': {
                        'id': new_card.id,
                        'name': new_card.name,
                        'desc': new_card.description,
                        'due_date': new_card.due_date.isoformat() if new_card.due_date else None
                    }
                })
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)

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