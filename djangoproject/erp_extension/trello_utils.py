# trello_utils.py
from trello import TrelloClient
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from datetime import datetime
from datetime import datetime, timezone

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
    
    # Obtener solo listas no archivadas
    lists = [lst for lst in board.all_lists() if not lst.closed]
    cards = []
        
    for list_obj in lists:
        list_cards = [card for card in list_obj.list_cards() if not card.closed]
        for card in list_cards:
            # Manejar fechas con zona horaria consistentemente
            due_date = None
            due_date_passed = False
            
            if card.due_date:
                # Asegurar que la fecha tenga zona horaria (UTC)
                if card.due_date.tzinfo is None:
                    due_date = card.due_date.replace(tzinfo=timezone.utc)
                else:
                    due_date = card.due_date
                
                # Comparar con la hora actual (también en UTC)
                current_time = datetime.now(timezone.utc)
                due_date_passed = due_date < current_time
            
            cards.append({
                'id': card.id,
                'name': card.name,
                'desc': card.description,
                'url': card.url,
                'list_name': list_obj.name,
                'due_date': due_date,
                'due_date_passed': due_date_passed
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



def create_list(board_id, list_name):
    """Crea una nueva lista en un tablero específico"""
    client = get_trello_client()
    board = client.get_board(board_id)
    return board.add_list(list_name)

def create_card(list_id, card_name, card_desc="", due_date=None):
    """Crea una nueva tarjeta en una lista específica"""
    client = get_trello_client()
    trello_list = client.get_list(list_id)
    return trello_list.add_card(card_name, desc=card_desc, due=due_date)


def update_list(list_id, new_name):
    """Actualiza el nombre de una lista existente"""
    client = get_trello_client()
    trello_list = client.get_list(list_id)
    
    # Forma correcta de actualizar una lista en Py-Trello
    trello_list.set_name(new_name)
    return True

def update_card(card_id, new_name=None, new_desc=None, new_due_date=None):
    """Actualiza los datos de una tarjeta existente"""
    client = get_trello_client()
    card = client.get_card(card_id)
    
    if new_name is not None:
        card.set_name(new_name)
    if new_desc is not None:
        card.set_description(new_desc)
    
    # Manejo especial para la fecha de vencimiento
    if new_due_date is not None:
        if isinstance(new_due_date, str):
            try:
                # Parsear la fecha y añadir zona horaria UTC
                new_due_date = datetime.strptime(new_due_date, '%Y-%m-%dT%H:%M')
                new_due_date = new_due_date.replace(tzinfo=timezone.utc)
            except ValueError:
                try:
                    new_due_date = datetime.strptime(new_due_date, '%Y-%m-%d')
                    new_due_date = new_due_date.replace(tzinfo=timezone.utc)
                except ValueError as e:
                    raise ValueError(f"Formato de fecha no válido: {new_due_date}") from e
        
        card.set_due(new_due_date)
    
    return {
        'id': card.id,
        'name': card.name,
        'desc': card.description,
        'due_date': card.due_date.replace(tzinfo=timezone.utc) if card.due_date else None
    }

def delete_card(card_id):
    """Elimina una tarjeta específica"""
    client = get_trello_client()
    card = client.get_card(card_id)
    card.delete()
    return True

def archive_list(list_id):
    """Archiva una lista específica"""
    client = get_trello_client()
    trello_list = client.get_list(list_id)
    trello_list.close()
    return True

def archive_board(board_id):
    """Archiva un tablero específico"""
    client = get_trello_client()
    board = client.get_board(board_id)
    board.close()
    return True