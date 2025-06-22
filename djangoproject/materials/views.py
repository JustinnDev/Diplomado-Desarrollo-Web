from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Material, Client, MaterialReception
from .forms import MaterialForm, ClientForm, MaterialReceptionForm
from django.contrib import messages

# Vistas para Materiales
class MaterialListView(ListView):
    model = Material
    template_name = 'materials/material_list.html'
    context_object_name = 'materials'

    def form_invalid(self, form):
        messages.error(self.request, 'No hay materiales disponibles.')
        return super().form_invalid(form)
   

class MaterialCreateView(CreateView):
    model = Material
    form_class = MaterialForm
    template_name = 'materials/material_form.html'
    success_url = reverse_lazy('materials:list')

    def form_valid(self, form):
        messages.success(self.request, 'Material creado correctamente.')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Error al crear el material. Por favor, corrige los errores.')
        return super().form_invalid(form)

class MaterialUpdateView(UpdateView):
    model = Material
    form_class = MaterialForm
    template_name = 'materials/material_form.html'
    success_url = reverse_lazy('materials:list')

    def form_valid(self, form):
        messages.success(self.request, 'Material actualizado correctamente.')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Error al actualizar el material. Por favor, corrige los errores.')
        return super().form_invalid(form)


class MaterialDeleteView(DeleteView):
    model = Material
    template_name = 'materials/material_confirm_delete.html'
    success_url = reverse_lazy('materials:list')

    def dispatch(self, request, *args, **kwargs):
        if request.method == 'POST':
            messages.success(request, 'Material eliminado correctamente.')
        return super().dispatch(request, *args, **kwargs)

# Vistas para Clientes
class ClientListView(ListView):
    model = Client
    template_name = 'materials/client_list.html'
    context_object_name = 'clients'

class ClientCreateView(CreateView):
    model = Client
    form_class = ClientForm
    template_name = 'materials/client_form.html'
    success_url = reverse_lazy('materials:client_list')



# Vistas para Recepción de Materiales
def reception_create(request):

    return render(request, 'comming_soon.html')

    if request.method == 'POST':
        form = MaterialReceptionForm(request.POST)
        if form.is_valid():
            reception = form.save(commit=False)
            material = form.cleaned_data['material']
            reception.unit_price = material.base_price
            reception.save()
            return redirect('materials:reception_list')
    else:
        form = MaterialReceptionForm()
    
    return render(request, 'materials/reception_form.html', {'form': form})

class ReceptionListView(ListView):
    model = MaterialReception
    template_name = 'materials/reception_list.html'
    context_object_name = 'receptions'
    ordering = ['-reception_date']
    paginate_by = 20

def reception_detail(request, pk):
    reception = get_object_or_404(MaterialReception, pk=pk)
    return render(request, 'materials/reception_detail.html', {'reception': reception})

def dashboard(request):
    return render(request, 'materials/material_dashboard.html')
