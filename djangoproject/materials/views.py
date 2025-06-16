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

class MaterialCreateView(CreateView):
    model = Material
    form_class = MaterialForm
    template_name = 'materials/material_form.html'
    success_url = reverse_lazy('materials:material_list')

class MaterialUpdateView(UpdateView):
    model = Material
    form_class = MaterialForm
    template_name = 'materials/material_form.html'
    success_url = reverse_lazy('materials:list')

class MaterialDeleteView(DeleteView):
    model = Material
    template_name = 'materials/material_confirm_delete.html'
    success_url = reverse_lazy('materials:list')

def add_material(request):
    if request.method == 'POST':
        form = MaterialForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('materials:list')
        else:
            messages.error(request, 'Error al guardar el material. Por favor, corrige los errores.')
    else:
        form = MaterialForm()
    
    return render(request, 'materials/material_form.html', {'form': form})

def edit_material(request, pk):
    material = get_object_or_404(Material, pk=pk)
    if request.method == 'POST':
        form = MaterialForm(request.POST, instance=material)
        if form.is_valid():
            form.save()
            messages.success(request, 'Material actualizado correctamente.')
            return redirect('materials:list')
        else:
            messages.error(request, 'Error al actualizar el material. Por favor, corrige los errores.')
    else:
        form = MaterialForm(instance=material)
    return render(request, 'materials/material_form.html', {'form': form})

def delete_material(request, pk):
    material = get_object_or_404(Material, pk=pk)
    if request.method == 'POST':
        material.delete()
        messages.success(request, 'Material eliminado correctamente.')
        return redirect('materials:list')
    return render(request, 'materials/material_confirm_delete.html', {'material': material})

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
