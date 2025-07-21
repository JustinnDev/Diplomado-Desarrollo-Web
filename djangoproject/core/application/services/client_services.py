from core.domain.use_cases import ClientUseCases
from core.infrastructure.persistence.django_orm import DjangoClientRepository

class ClientService:
    def __init__(self):
        self.use_cases = ClientUseCases(DjangoClientRepository())
    
    def create_client(self, client_data):
        return self.use_cases.create_client(client_data)
    
    def get_client(self, client_id):
        return self.use_cases.get_client(client_id)