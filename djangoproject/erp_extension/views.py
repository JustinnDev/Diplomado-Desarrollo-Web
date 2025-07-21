from django.shortcuts import render
from django.contrib import messages
import pymysql 
from django.http import JsonResponse
from django.views import View
from .trello_utils import verify_trello_connection, get_all_workspaces, get_boards_by_workspace, get_board_details, create_list, create_card, delete_card, archive_list, archive_board, update_list, update_card
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DetailView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from decimal import Decimal
from django.core.exceptions import ValidationError

from .models import (
    Driver, Vehicle, FuelStation, 
    FuelRefill, FuelConsumption, MaintenanceLog
)
from .forms import (
    DriverForm, VehicleForm, FuelStationForm,
    FuelRefillForm, FuelConsumptionForm, MaintenanceLogForm
)


class TrelloConnectionTestView(View):
    def get(self, request):
        """
        Vista para probar la conexión con Trello y mostrar resultados en HTML
        """
        test_result = verify_trello_connection()
        
        context = {
            'test_result': test_result,
            'page_title': 'Prueba de conexión con Trello'
        }
        
        return render(request, 'erp_extension/crm.html', context)

# views.py (modificar la clase TrelloExplorerView)

class TrelloExplorerView(TemplateView):
    template_name = 'erp_extension/crm.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        workspace_id = self.kwargs.get('workspace_id')
        board_id = self.kwargs.get('board_id')
        
        try:
            if board_id:
                context['board'] = get_board_details(board_id)
                context['view_type'] = 'board_detail'
            elif workspace_id:
                context['boards'] = get_boards_by_workspace(workspace_id)
                context['current_workspace_id'] = workspace_id
                context['view_type'] = 'workspace_boards'
            else:
                context['workspaces'] = get_all_workspaces()
                context['view_type'] = 'workspaces'
                
        except Exception as e:
            context['error'] = str(e)
            
        return context
    
    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')
        board_id = kwargs.get('board_id')
        
        try:
            if action == 'create_list':
                list_name = request.POST.get('list_name')
                new_list = create_list(board_id, list_name)
                return JsonResponse({
                    'success': True,
                    'list': {
                        'id': new_list.id,
                        'name': new_list.name
                    }
                })
                
            elif action == 'create_card':
                list_id = request.POST.get('list_id')
                card_name = request.POST.get('card_name')
                card_desc = request.POST.get('card_desc', '')
                due_date = request.POST.get('due_date')
                
                new_card = create_card(
                    list_id, 
                    card_name, 
                    card_desc, 
                    due_date if due_date else None
                )
                
                return JsonResponse({
                    'success': True,
                    'card': {
                        'id': new_card.id,
                        'name': new_card.name,
                        'desc': new_card.description,
                        'due_date': new_card.due_date.isoformat() if new_card.due_date else None
                    }
                })
            
            elif action == 'update_list':
                list_id = request.POST.get('list_id')
                new_name = request.POST.get('new_name')
                update_list(list_id, new_name)
                return JsonResponse({'success': True})
                
            elif action == 'update_card':
                card_id = request.POST.get('card_id')
                new_name = request.POST.get('new_name')
                new_desc = request.POST.get('new_desc', None)
                new_due_date = request.POST.get('new_due_date', None)
                
                # Convertir descripción vacía a None
                if new_desc == '':
                    new_desc = None
                    
                try:
                    updated_card = update_card(
                        card_id,
                        new_name,
                        new_desc,
                        new_due_date if new_due_date else None
                    )
                    
                    # Manejar correctamente la fecha en la respuesta
                    due_date_response = None
                    if updated_card['due_date']:
                        if hasattr(updated_card['due_date'], 'isoformat'):
                            due_date_response = updated_card['due_date'].isoformat()
                        else:
                            due_date_response = str(updated_card['due_date'])
                    
                    return JsonResponse({
                        'success': True,
                        'card': {
                            'id': updated_card['id'],
                            'name': updated_card['name'],
                            'desc': updated_card['desc'],
                            'due_date': due_date_response
                        }
                    })
            
                except Exception as e:
                    return JsonResponse({
                        'success': False,
                        'error': str(e)
                    }, status=400)
                
            elif action == 'delete_card':
                card_id = request.POST.get('card_id')
                delete_card(card_id)
                return JsonResponse({'success': True})
                
            elif action == 'archive_list':
                list_id = request.POST.get('list_id')
                archive_list(list_id)
                return JsonResponse({'success': True})
                
            elif action == 'archive_board':
                archive_board(board_id)
                return JsonResponse({'success': True})
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
            


def view_clients(request):
    print("\n=== CONEXIÓN MYSQL 2005 ===")
    messages.info(request, "Iniciando conexión con el ERP")

    try:
        conn = pymysql.connect(
            host='26.110.109.182',
            user='root',
            password='',
            database='dpadmwin',
            charset='latin1',
            connect_timeout=10
        )
        print("✓ Conexión via pymysql exitosa")

        cursor = conn.cursor()
        messages.success(request, "Conexión establecida")

        # Consulta compatible
        query = "SELECT * FROM dpclientes LIMIT 50"
        print(f"Ejecutando: {query}")
        cursor.execute(query)
        
        columnas = [desc[0] for desc in cursor.description]
        datos = cursor.fetchall()
        
        print(f"✓ Obtenidos {len(datos)} registros")
        messages.success(request, f"Datos cargados ({len(datos)} registros)")
        
        conn.close()
        return render(request, 'erp_extension/ver_dpclientes.html', {
            'columnas': columnas,
            'datos': datos
        })

    except Exception as e:
        error_type = type(e).__name__
        error_msg = str(e.args[1]) if len(e.args) > 1 else str(e)
        print(f"✗ ERROR ({error_type}): {error_msg}")
        
        messages.error(request, "Error al acceder al ERP")
        messages.warning(request, f"Detalle: {error_msg.split('(')[0]}")
        
        return render(request, 'erp_extension/ver_dpclientes.html', {
            'columnas': [],
            'datos': []
        })
    finally:
        print("=== FIN DE EJECUCIÓN ===")















class BaseFuelView(View):
    """Vista base con funcionalidad común para todas las vistas de combustible"""
    success_message = ""
    error_message = ""

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if hasattr(self, 'get_success_message') and self.success_message:
            messages.success(request, self.success_message)
        elif hasattr(self, 'get_error_message') and self.error_message:
            messages.error(request, self.error_message)
        return response

# Vistas para Conductores
class DriverListView(BaseFuelView, ListView):
    model = Driver
    template_name = 'erp_extension/driver_list.html'
    context_object_name = 'drivers'
    success_message = "Lista de conductores cargada correctamente"

class DriverCreateView(BaseFuelView, CreateView):
    model = Driver
    form_class = DriverForm
    template_name = 'erp_extension/driver_form.html'
    success_url = reverse_lazy('erp_extension:driver_list')
    success_message = "Conductor creado exitosamente"
    error_message = "Error al crear el conductor"

class DriverUpdateView(BaseFuelView, UpdateView):
    model = Driver
    form_class = DriverForm
    template_name = 'erp_extension/driver_form.html'
    success_url = reverse_lazy('erp_extension:driver_list')
    success_message = "Conductor actualizado exitosamente"
    error_message = "Error al actualizar el conductor"

# Vistas para Vehículos
class VehicleListView(BaseFuelView, ListView):
    model = Vehicle
    template_name = 'erp_extension/vehicle_list.html'
    context_object_name = 'vehicles'
    success_message = "Lista de vehículos cargada correctamente"

class VehicleCreateView(BaseFuelView, CreateView):
    model = Vehicle
    form_class = VehicleForm
    template_name = 'erp_extension/vehicle_form.html'
    success_url = reverse_lazy('erp_extension:vehicle_list')
    success_message = "Vehículo creado exitosamente"
    error_message = "Error al crear el vehículo"

class VehicleUpdateView(BaseFuelView, UpdateView):
    model = Vehicle
    form_class = VehicleForm
    template_name = 'erp_extension/vehicle_form.html'
    success_url = reverse_lazy('erp_extension:vehicle_list')
    success_message = "Vehículo actualizado exitosamente"
    error_message = "Error al actualizar el vehículo"


class VehicleDetailView(BaseFuelView, DetailView):
    model = Vehicle
    template_name = 'erp_extension/vehicle_detail.html'
    context_object_name = 'vehicle'
    success_message = "Detalles del vehículo cargados correctamente"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vehicle = self.get_object()
        
        # Obtener los registros relacionados
        context['refills'] = FuelRefill.objects.filter(vehicle=vehicle).order_by('-date')[:5]
        context['consumptions'] = FuelConsumption.objects.filter(vehicle=vehicle).order_by('-date')[:5]
        context['maintenances'] = MaintenanceLog.objects.filter(vehicle=vehicle).order_by('-date')[:5]
        
        # Calcular el porcentaje del nivel de combustible (manejo seguro de Decimal)
        try:
            if vehicle.fuel_capacity > Decimal('0'):
                fuel_percentage = (vehicle.current_fuel_level / vehicle.fuel_capacity) * Decimal('100')
            else:
                fuel_percentage = Decimal('0')
        except (TypeError, ValueError):
            fuel_percentage = Decimal('0')
            
        context['fuel_percentage'] = float(fuel_percentage)  # Convertimos a float para el template
        
        return context

# Vistas para Estaciones de Combustible
class FuelStationListView(BaseFuelView, ListView):
    model = FuelStation
    template_name = 'erp_extension/fuelstation_list.html'
    context_object_name = 'fuelstations'
    success_message = "Lista de estaciones de combustible cargada correctamente"

class FuelStationCreateView(BaseFuelView, CreateView):
    model = FuelStation
    form_class = FuelStationForm
    template_name = 'erp_extension/fuelstation_form.html'
    success_url = reverse_lazy('erp_extension:fuelstation_list')
    success_message = "Estación de combustible creada exitosamente"
    error_message = "Error al crear la estación de combustible"

# Vistas para Recargas de Combustible

class FuelRefillCreateView(BaseFuelView, CreateView):
    model = FuelRefill
    form_class = FuelRefillForm
    template_name = 'erp_extension/fuelrefill_form.html'
    success_message = "Recarga de combustible registrada exitosamente"
    error_message = "Error al registrar la recarga de combustible"

    def get_success_url(self):
        return reverse_lazy('erp_extension:vehicle_detail', kwargs={'pk': self.object.vehicle.pk})

    def get_initial(self):
        initial = super().get_initial()
        vehicle_id = self.request.GET.get('vehicle_id')
        if vehicle_id:
            initial['vehicle'] = get_object_or_404(Vehicle, pk=vehicle_id)
        return initial

    def form_valid(self, form):
        # Validar que la recarga no exceda la capacidad máxima del vehículo
        vehicle = form.cleaned_data['vehicle']
        refill_quantity = form.cleaned_data['quantity']
        current_level = vehicle.current_fuel_level or 0
        fuel_capacity = vehicle.fuel_capacity

        if current_level + refill_quantity > fuel_capacity:
            form.add_error('quantity', f"La recarga excede la capacidad actual del Tanque.")
            return self.form_invalid(form)
        return super().form_valid(form)

class FuelRefillListView(BaseFuelView, ListView):
    model = FuelRefill
    template_name = 'erp_extension/fuelrefill_list.html'
    context_object_name = 'refills'
    paginate_by = 20
    success_message = "Lista de recargas de combustible cargada correctamente"

    def get_queryset(self):
        queryset = super().get_queryset()
        vehicle_id = self.request.GET.get('vehicle_id')
        if vehicle_id:
            queryset = queryset.filter(vehicle__id=vehicle_id)
        return queryset.order_by('-date')

# Vistas para Consumo de Combustible
class FuelConsumptionCreateView(BaseFuelView, CreateView):
    model = FuelConsumption
    form_class = FuelConsumptionForm
    template_name = 'erp_extension/fuelconsumption_form.html'
    success_message = "Consumo de combustible registrado exitosamente"
    error_message = "Error al registrar el consumo de combustible"

    def get_success_url(self):
        return reverse_lazy('erp_extension:vehicle_detail', kwargs={'pk': self.object.vehicle.pk})

    def get_initial(self):
        initial = super().get_initial()
        vehicle_id = self.request.GET.get('vehicle_id')
        if vehicle_id:
            initial['vehicle'] = get_object_or_404(Vehicle, pk=vehicle_id)
        return initial
    
    def form_valid(self, form):
        # Validar que el consumo no genere un nivel negativo del tanque
        vehicle = form.cleaned_data['vehicle']
        consumption_quantity = form.cleaned_data['quantity']
        current_level = vehicle.current_fuel_level or 0

        if consumption_quantity > current_level:
            form.add_error('quantity', "El consumo no puede ser negativo.")
            return self.form_invalid(form)
        return super().form_valid(form)

class FuelConsumptionUpdateView(BaseFuelView, UpdateView):
    model = FuelConsumption
    form_class = FuelConsumptionForm
    template_name = 'erp_extension/fuelconsumption_form.html'
    success_message = "Consumo de combustible actualizado exitosamente"
    error_message = "Error al actualizar el consumo de combustible"

    def get_success_url(self):
        return reverse_lazy('erp_extension:vehicle_detail', kwargs={'pk': self.object.vehicle.pk})

    def get_initial(self):
        initial = super().get_initial()
        vehicle_id = self.request.GET.get('vehicle_id')
        if vehicle_id:
            initial['vehicle'] = get_object_or_404(Vehicle, pk=vehicle_id)
        return initial

# Vistas para Mantenimientos
class MaintenanceLogCreateView(BaseFuelView, CreateView):
    model = MaintenanceLog
    form_class = MaintenanceLogForm
    template_name = 'erp_extension/maintenance_form.html'
    success_message = "Mantenimiento registrado exitosamente"
    error_message = "Error al registrar el mantenimiento"

    def get_success_url(self):
        return reverse_lazy('erp_extension:vehicle_detail', kwargs={'pk': self.object.vehicle.pk})

    def get_initial(self):
        initial = super().get_initial()
        vehicle_id = self.request.GET.get('vehicle_id')
        if vehicle_id:
            initial['vehicle'] = get_object_or_404(Vehicle, pk=vehicle_id)
        return initial

class MaintenanceLogListView(BaseFuelView, ListView):
    model = MaintenanceLog
    template_name = 'erp_extension/maintenance_list.html'
    context_object_name = 'maintenances'
    paginate_by = 20
    success_message = "Lista de mantenimientos cargada correctamente"

    def get_queryset(self):
        queryset = super().get_queryset()
        vehicle_id = self.request.GET.get('vehicle_id')
        if vehicle_id:
            queryset = queryset.filter(vehicle__id=vehicle_id)
        return queryset.order_by('-date')
    
class MaintenanceLogDetailView(BaseFuelView, DetailView):
    model = MaintenanceLog
    template_name = 'erp_extension/maintenance_detail.html'
    context_object_name = 'maintenance'
    success_message = "Detalles de mantenimiento cargados correctamente"

class MaintenanceLogUpdateView(BaseFuelView, UpdateView):
    model = MaintenanceLog
    form_class = MaintenanceLogForm
    template_name = 'erp_extension/maintenance_form.html'
    success_message = "Mantenimiento actualizado exitosamente"
    error_message = "Error al actualizar el mantenimiento"

    def get_success_url(self):
        return reverse_lazy('erp_extension:vehicle_detail', kwargs={'pk': self.object.vehicle.pk})

# Vista de Dashboard
class FuelDashboardView(BaseFuelView, View):
    template_name = 'erp_extension/fuel_dashboard.html'
    success_message = "Dashboard de combustible cargado correctamente"

    def get(self, request, *args, **kwargs):
        vehicles = Vehicle.objects.filter(is_active=True)
        drivers = Driver.objects.filter(is_active=True)
        fuelstations = FuelStation.objects.filter(is_active=True)
        recent_refills = FuelRefill.objects.order_by('-date')[:5]
        recent_consumptions = FuelConsumption.objects.order_by('-date')[:5]
        
        context = {
            'vehicles': vehicles,
            'drivers': drivers,
            'fuelstations': fuelstations,
            'recent_refills': recent_refills,
            'recent_consumptions': recent_consumptions,
        }
        return render(request, self.template_name, context)
    
class FuelRefillUpdateView(BaseFuelView, UpdateView):
    model = FuelRefill
    form_class = FuelRefillForm
    template_name = 'erp_extension/fuelrefill_form.html'
    success_message = "Recarga de combustible actualizada exitosamente"
    error_message = "Error al actualizar la recarga de combustible"

    def get_success_url(self):
        # Redirige a la página de detalle del vehículo asociado
        return reverse_lazy('erp_extension:vehicle_detail', kwargs={'pk': self.object.vehicle.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Agrega el vehículo al contexto si está disponible en la URL
        if 'vehicle_id' in self.kwargs:
            context['vehicle'] = get_object_or_404(Vehicle, pk=self.kwargs['vehicle_id'])
        return context


class VehicleFuelRefillUpdateView(FuelRefillUpdateView):
    """
    Vista específica para editar recargas desde la página de un vehículo.
    Hereda de FuelRefillUpdateView y solo sobrecarga get_initial para
    asegurar la relación con el vehículo.
    """
    
    def get_initial(self):
        initial = super().get_initial()
        vehicle_id = self.kwargs.get('vehicle_id')
        if vehicle_id:
            vehicle = get_object_or_404(Vehicle, pk=vehicle_id)
            initial['vehicle'] = vehicle
            initial['driver'] = vehicle.current_driver  # Establece el conductor actual por defecto
        return initial
