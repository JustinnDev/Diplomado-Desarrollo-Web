from core.domain.repositories import ClientRepository
from core.domain.entities import Client
from materials.models import Client as ClientModel

class DjangoClientRepository(ClientRepository):
    def get_by_id(self, client_id):
        client = ClientModel.objects.get(pk=client_id)
        return Client(
            id=client.id,
            name=client.name,
            identification=client.identification,
            phone=client.phone,
            address=client.address
        )
    
    def save(self, client: Client):
        if client.id:
            client_model = ClientModel.objects.get(pk=client.id)
            client_model.name = client.name
            # Actualizar otros campos
            client_model.save()
        else:
            client_model = ClientModel.objects.create(
                name=client.name,
                identification=client.identification,
                phone=client.phone,
                address=client.address
            )
        return client_model.id