from core.domain.repositories import ClientRepository

class ClientUseCases:
    def __init__(self, client_repository: ClientRepository):
        self.client_repository = client_repository
    
    def create_client(self, client_data):
        # Validaciones de negocio aquí
        return self.client_repository.save(client_data)
    
    def get_client(self, client_id):
        return self.client_repository.get_by_id(client_id)
    
    def get_all_clients(self):
        return self.client_repository.get_all()