from abc import ABC, abstractmethod
from core.domain.entities import Client

class ClientRepository(ABC):
    @abstractmethod
    def get_by_id(self, client_id):
        pass
    
    @abstractmethod
    def get_all(self):
        pass
    
    @abstractmethod
    def save(self, client: Client):
        pass
    
    @abstractmethod
    def delete(self, client_id):
        pass