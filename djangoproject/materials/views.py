from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView, View, DetailView
from django.urls import reverse_lazy
from .models import MaterialType, Client, MaterialReception, ReceptionMaterial, MaterialOperation
from .forms import MaterialTypeForm, ClientForm
from django.contrib import messages
from django.db import transaction

# Vistas para Materiales
class MaterialListView(ListView):
    model = MaterialType
    template_name = 'materials/material_list.html'
    context_object_name = 'materials'

    def form_invalid(self, form):
        messages.error(self.request, 'No hay materiales disponibles.')
        return super().form_invalid(form)
   

class MaterialCreateView(CreateView):
    model = MaterialType
    form_class = MaterialTypeForm
    template_name = 'materials/material_form.html'
    success_url = reverse_lazy('materials:list')

    def form_valid(self, form):
        messages.success(self.request, 'Material creado correctamente.')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Error al crear el material. Por favor, corrige los errores.')
        return super().form_invalid(form)

class MaterialUpdateView(UpdateView):
    model = MaterialType
    form_class = MaterialTypeForm
    template_name = 'materials/material_form.html'
    success_url = reverse_lazy('materials:list')

    def form_valid(self, form):
        messages.success(self.request, 'Material actualizado correctamente.')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Error al actualizar el material. Por favor, corrige los errores.')
        return super().form_invalid(form)


class MaterialDeleteView(DeleteView):
    model = MaterialType
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

class ReceptionCreateView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'materials/reception_create.html', {
            'clients': Client.objects.all(),
            'material_types': MaterialType.objects.all()
        })

    def post(self, request, *args, **kwargs):
        print("POST data received:", request.POST)
        try:
            with transaction.atomic():
                # 1. Crear Recepción
                print("Creando MaterialReception...")
                reception = MaterialReception.objects.create(
                    client_id=request.POST.get('client'),
                    notes=request.POST.get('notes', '')
                )
                print("Recepción creada con ID:", reception.id)

                # 2. Procesar Materiales (estructura: materials[0][type], materials[0][operations][0][gross], etc.)
                material_keys = [k.split('[')[1].split(']')[0] for k in request.POST if k.startswith('materials[')]
                material_indices = sorted(list(set(material_keys)))
                print("Material indices encontrados:", material_indices)

                for index in material_indices:
                    print(f"Procesando material index: {index}")
                    # 2.1. Crear ReceptionMaterial
                    material_type_id = request.POST.get(f'materials[{index}][type]')
                    subtype = request.POST.get(f'materials[{index}][subtype]', 'LIMPIO')
                    discount_type = request.POST.get(f'materials[{index}][discount_type]', 'NONE')
                    discount_value = request.POST.get(f'materials[{index}][discount_value]', 0)
                    print(f"Datos del material: type={material_type_id}, subtype={subtype}, discount_type={discount_type}, discount_value={discount_value}")

                    material = ReceptionMaterial.objects.create(
                        reception=reception,
                        material_type_id=material_type_id,
                        subtype=subtype,
                        discount_type=discount_type,
                        discount_value=discount_value
                    )
                    print("ReceptionMaterial creado con ID:", material.id)

                    # 2.2. Procesar Operaciones
                    operation_keys = [k.split('[')[3].split(']')[0] 
                                    for k in request.POST 
                                    if f'materials[{index}][operations]' in k]
                    operation_indices = sorted(list(set(operation_keys)))
                    print(f"Operaciones encontradas para material {index}:", operation_indices)

                    for op_index in operation_indices:
                        gross_weight = request.POST.get(f'materials[{index}][operations][{op_index}][gross]')
                        tare_weight = request.POST.get(f'materials[{index}][operations][{op_index}][tare]')
                        print(f"Creando MaterialOperation para material {index}, operación {op_index}: gross={gross_weight}, tare={tare_weight}")
                        MaterialOperation.objects.create(
                            reception_material=material,
                            gross_weight=gross_weight,
                            tare_weight=tare_weight
                        )

                print("Recepción y materiales guardados correctamente.")
                messages.success(request, '¡Recepción guardada correctamente!')
                return redirect('materials:reception_detail', pk=reception.id)

        except Exception as e:
            print("Error en la creación de la recepción:", str(e))
            messages.error(request, f'Error: {str(e)}')
            return redirect('materials:reception_create')


class ReceptionDetailView(DetailView):
    model = MaterialReception
    template_name = 'materials/reception_detail.html'
    context_object_name = 'reception'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        reception = self.object
        
        # Calcular totales
        total_net_weight = sum(material.net_weight for material in reception.materials.all())
        operation_count = sum(material.operations.count() for material in reception.materials.all())
        total_reception = sum(material.total for material in reception.materials.all())
        
        context.update({
            'total_net_weight': total_net_weight,
            'operation_count': operation_count,
            'total_reception': total_reception,
        })
        return context

class ReceptionCompleteView(TemplateView):
    def get(self, request, *args, **kwargs):
        if 'current_reception' in request.session:
            reception_id = request.session['current_reception']
            reception = MaterialReception.objects.get(pk=reception_id)
            
            # Verificar que tenga al menos un material con operaciones
            if reception.materials.exists():
                messages.success(request, 'Recepción completada y guardada correctamente.')
            else:
                messages.warning(request, 'Recepción cancelada: No se añadieron materiales.')
            
            del request.session['current_reception']
        
        if 'current_material' in request.session:
            del request.session['current_material']
            
        return redirect('materials:reception_list')