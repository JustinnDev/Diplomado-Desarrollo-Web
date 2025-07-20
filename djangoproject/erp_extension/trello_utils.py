# trello_utils.py
from trello import TrelloClient
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

def verify_trello_connection():
    """
    Verifica la conexión con Trello y devuelve información básica si es exitosa.
    """
    try:
        # Verificar que las credenciales están configuradas
        if not all([settings.TRELLO_API_KEY, settings.TRELLO_API_SECRET, settings.TRELLO_TOKEN]):
            raise ImproperlyConfigured("Faltan credenciales de Trello en settings.py")
        
        client = TrelloClient(
            api_key=settings.TRELLO_API_KEY,
            api_secret=settings.TRELLO_API_SECRET,
            token=settings.TRELLO_TOKEN
        )
        
        boards = client.list_boards()
        first_board = boards[0] if boards else None
        
        return {
            'success': True,
            'message': 'Conexión exitosa con Trello',
            'details': {
                'board_name': first_board.name if first_board else 'No hay tableros',
                'board_id': first_board.id if first_board else 'N/A',
                'total_boards': len(boards),
                'api_key': settings.TRELLO_API_KEY[:4] + '...' + settings.TRELLO_API_KEY[-4:] if settings.TRELLO_API_KEY else 'No configurada'
            }
        }
            
    except Exception as e:
        return {
            'success': False,
            'message': 'Error de conexión con Trello',
            'details': str(e)
        }
    


def get_trello_client():
    """Obtiene el cliente de Trello configurado"""
    if not all([settings.TRELLO_API_KEY, settings.TRELLO_API_SECRET, settings.TRELLO_TOKEN]):
        raise ImproperlyConfigured("Faltan credenciales de Trello en settings.py")
    
    return TrelloClient(
        api_key=settings.TRELLO_API_KEY,
        api_secret=settings.TRELLO_API_SECRET,
        token=settings.TRELLO_TOKEN
    )

def get_all_workspaces():
    """Obtiene todos los espacios de trabajo (organizaciones)"""
    client = get_trello_client()
    return client.fetch_json('/members/me/organizations')

def get_boards_by_workspace(workspace_id):
    """Obtiene todos los tableros de un espacio de trabajo"""
    client = get_trello_client()
    return client.fetch_json(
        f'/organizations/{workspace_id}/boards',
        query_params={'fields': 'name,desc,url,closed,dateLastActivity'}
    )

def get_board_details(board_id):
    """Obtiene detalles completos de un tablero"""
    client = get_trello_client()
    board = client.get_board(board_id)
    
    # Obtener listas y tarjetas
    lists = board.all_lists()
    cards = []
    
    for list_obj in lists:
        list_cards = list_obj.list_cards()
        for card in list_cards:
            cards.append({
                'id': card.id,
                'name': card.name,
                'desc': card.description,
                'url': card.url,
                'list_name': list_obj.name,
                'due_date': card.due_date
            })
    
    return {
        'id': board.id,
        'name': board.name,
        'description': board.description,
        'url': board.url,
        'closed': board.closed,
        'last_activity': board.date_last_activity,
        'lists': [{'id': l.id, 'name': l.name} for l in lists],
        'cards': cards
    }