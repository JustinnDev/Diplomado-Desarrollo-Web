from django.views import View
from django.shortcuts import render, redirect
from core.application.services import ClientService

class ClientController(View):
    def __init__(self):
        self.client_service = ClientService()
    
    def get(self, request):
        clients = self.client_service.get_all_clients()
        return render(request, 'clients/list.html', {'clients': clients})
    
    def post(self, request):
        client_data = {
            'name': request.POST.get('name'),
            'identification': request.POST.get('identification'),
            'phone': request.POST.get('phone'),
            'address': request.POST.get('address')
        }
        self.client_service.create_client(client_data)
        return redirect('clients:list')