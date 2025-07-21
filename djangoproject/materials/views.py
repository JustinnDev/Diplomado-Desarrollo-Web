from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView, View, DetailView
from django.urls import reverse_lazy
from .models import MaterialType, Client, MaterialReception, ReceptionMaterial, MaterialOperation
from .forms import MaterialTypeForm, ClientForm
from django.contrib import messages
from django.contrib.auth.mixins import AccessMixin
from django.db import transaction, connections
from django.core.serializers.json import DjangoJSONEncoder
import json
from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib.enums import TA_LEFT



def admin_or_lin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('landing:index')
        
        if request.user.role in ['admin', 'licenciado']:
            return view_func(request, *args, **kwargs)
        return redirect('landing:index')
    return wrapper

class AdminMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('landing:index')
        
        if request.user.role not in ['admin', 'licenciado']:
            return redirect('landing:index')
            
        return super().dispatch(request, *args, **kwargs)


class MaterialStockView(AdminMixin, ListView):
    model = MaterialType
    template_name = 'materials/material_stock.html'
    context_object_name = 'materials'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.order_by('category', 'name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        materials = context['materials']
        total_stock = 0
        total_value = 0
        
        for material in materials:
            stock = material.current_stock
            total_stock += stock
            total_value += stock * material.base_price
        
        context['total_stock'] = total_stock
        context['total_value'] = total_value
        
        return context

# Vistas para Materiales
class MaterialListView(AdminMixin,ListView):
    model = MaterialType
    template_name = 'materials/material_list.html'
    context_object_name = 'materials'

    def form_invalid(self, form):
        messages.error(self.request, 'No hay materiales disponibles.')
        return super().form_invalid(form)
   
class MaterialCreateView(AdminMixin,CreateView):
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

class MaterialUpdateView(AdminMixin,UpdateView):
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

class MaterialDeleteView(AdminMixin,DeleteView):
    model = MaterialType
    template_name = 'materials/material_confirm_delete.html'
    success_url = reverse_lazy('materials:list')

    def dispatch(self, request, *args, **kwargs):
        if request.method == 'POST':
            messages.success(request, 'Material eliminado correctamente.')
        return super().dispatch(request, *args, **kwargs)



# Vistas para Clientes
class ClientListView(AdminMixin,ListView):
    model = Client
    template_name = 'materials/client_list.html'
    context_object_name = 'clients'

class ClientCreateView(AdminMixin,CreateView):
    model = Client
    form_class = ClientForm
    template_name = 'materials/client_form.html'
    success_url = reverse_lazy('materials:client_list')



# Vistas para Recepción de Materiales
def comming_soon(request):
    return render(request, 'comming_soon.html')

class ReceptionListView(AdminMixin,ListView):
    model = MaterialReception
    template_name = 'materials/reception_list.html'
    context_object_name = 'receptions'
    ordering = ['-reception_date']
    paginate_by = 20

@admin_or_lin_required
def reception_detail(request, pk):
    reception = get_object_or_404(MaterialReception, pk=pk)
    return render(request, 'materials/reception_detail.html', {'reception': reception})

@admin_or_lin_required
def dashboard(request):
    return render(request, 'materials/material_dashboard.html')

class ReceptionCreateView(AdminMixin,View):
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

class ReceptionUpdateView(AdminMixin,View):
    def get(self, request, pk, *args, **kwargs):
        reception = get_object_or_404(MaterialReception, pk=pk)
        
        # Prepara los datos de materiales con sus operaciones
        materials_data = []
        for material in reception.materials.all().prefetch_related('operations'):
            material_data = {
                'material_type': {
                    'id': material.material_type.id,
                    'name': material.material_type.name,
                    'base_price': str(material.material_type.base_price)
                },
                'subtype': material.subtype,
                'discount_type': material.discount_type,
                'discount_value': str(material.discount_value),
                'operations': [
                    {
                        'gross_weight': str(op.gross_weight),
                        'tare_weight': str(op.tare_weight)
                    }
                    for op in material.operations.all()
                ]
            }
            materials_data.append(material_data)
        
        context = {
            'reception': reception,
            'clients': Client.objects.all(),
            'material_types': MaterialType.objects.all(),
            'editing': True,
            'materials_json': json.dumps(materials_data)
        }

        print("Rendering reception update with context:", context)
        
        return render(request, 'materials/reception_create.html', context)

    def post(self, request, pk, *args, **kwargs):
        print("POST data received for update:", request.POST)
        reception = get_object_or_404(MaterialReception, pk=pk)
        
        try:
            with transaction.atomic():
                # 1. Actualizar Recepción
                print("Actualizando MaterialReception...")
                reception.client_id = request.POST.get('client')
                reception.notes = request.POST.get('notes', '')
                reception.save()
                print("Recepción actualizada")

                # 2. Eliminar materiales existentes (y sus operaciones se borran en cascada)
                reception.materials.all().delete()
                print("Materiales anteriores eliminados")

                # 3. Procesar Materiales (igual que en create)
                material_keys = [k.split('[')[1].split(']')[0] for k in request.POST if k.startswith('materials[')]
                material_indices = sorted(list(set(material_keys)))
                print("Material indices encontrados:", material_indices)

                for index in material_indices:
                    print(f"Procesando material index: {index}")
                    # 3.1. Crear ReceptionMaterial
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

                    # 3.2. Procesar Operaciones
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

                print("Recepción y materiales actualizados correctamente.")
                messages.success(request, '¡Recepción actualizada correctamente!')
                return redirect('materials:reception_detail', pk=reception.id)

        except Exception as e:
            print("Error en la actualización de la recepción:", str(e))
            messages.error(request, f'Error: {str(e)}')
            return redirect('materials:reception_update', pk=pk)

class ReceptionDeleteView(AdminMixin,DeleteView):
    model = MaterialReception
    template_name = 'materials/reception_confirm_delete.html'
    success_url = reverse_lazy('materials:reception_list')

    def dispatch(self, request, *args, **kwargs):
        if request.method == 'POST':
            messages.success(request, 'Recepción eliminada correctamente.')
        return super().dispatch(request, *args, **kwargs)

class ReceptionDetailView(AdminMixin,DetailView):
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

class ReceptionCompleteView(AdminMixin,TemplateView):
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
    


class ReceptionPrintView(AdminMixin, View):
    def get(self, request, pk, *args, **kwargs):
        reception = get_object_or_404(MaterialReception, pk=pk)

        total_net_weight = sum(material.net_weight for material in reception.materials.all())
        total_reception = sum(material.total for material in reception.materials.all())

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Recibo_Recepción_{reception.id}.pdf"'

        doc = SimpleDocTemplate(response, pagesize=letter,
                                rightMargin=36, leftMargin=36,
                                topMargin=36, bottomMargin=36)

        styles = getSampleStyleSheet()
        elements = []

        # Estilos personalizados
        left_title_style = ParagraphStyle('LeftTitle', parent=styles['Heading1'], fontSize=16, alignment=TA_LEFT, spaceAfter=6, textColor=colors.HexColor('#2c3e50'), fontName='Helvetica-Bold')
        left_subtitle_style = ParagraphStyle('LeftSubtitle', parent=styles['Normal'], fontSize=10, alignment=TA_LEFT, spaceAfter=4, textColor=colors.HexColor('#34495e'), fontName='Helvetica')
        section_style = ParagraphStyle('Section', parent=styles['Heading3'], fontSize=12, spaceAfter=8, textColor=colors.HexColor('#3498db'), fontName='Helvetica-Bold')
        total_style = ParagraphStyle('Total', parent=styles['Normal'], fontSize=12, alignment=TA_RIGHT, textColor=colors.HexColor('#c0392b'), fontName='Helvetica-Bold')

        # ENCABEZADO alineado a la izquierda
        elements.append(Paragraph("RECIBO DE RECEPCIÓN", left_title_style))
        elements.append(Paragraph(f"N° {reception.id:05d}", left_subtitle_style))
        elements.append(Spacer(1, 6))
        elements.append(Paragraph("RECICLADORA TITANIUM C.A.", left_subtitle_style))
        elements.append(Paragraph("Aragua Av. Joaquin Crespo Calle de Servicio", left_subtitle_style))
        elements.append(Paragraph("Parcela Nro. 25-B-G-4 Caserio Asentamiento Campesino La Morita Turmero", left_subtitle_style))
        elements.append(Paragraph("RIF: J-412345678 | Teléfono: 0243-1234567", left_subtitle_style))
        elements.append(Paragraph("Email: administracion@recicladoratitanium.com", left_subtitle_style))
        elements.append(Spacer(1, 16))

        # INFORMACIÓN GENERAL
        elements.append(Paragraph("INFORMACIÓN GENERAL", section_style))

        general_data = [
            ["Cliente:", reception.client.name, "Fecha/Hora:", reception.reception_date.strftime("%d/%m/%Y %H:%M")],
            ["Identificación:", reception.client.identification, "Total Recepción:", f"${total_reception:,.2f}"],
        ]

        if reception.client.phone:
            general_data.append(["Teléfono:", reception.client.phone, "Peso Total:", f"{total_net_weight:,.2f} kg"])

        if reception.notes:
            general_data.append(["Notas:", reception.notes, "", ""])

        general_table = Table(general_data, colWidths=[80, 180, 80, 180])
        general_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c3e50')),
        ]))
        elements.append(general_table)
        elements.append(Spacer(1, 24))

        # DETALLE DE MATERIALES
        elements.append(Paragraph("DETALLE DE MATERIALES RECEPCIONADOS", section_style))

        material_data = [[
            "Material", 
            "Categoría", 
            "Subtipo", 
            "Precio Unit.", 
            "Desc.", 
            "Peso Neto", 
            "Total"
        ]]

        for material in reception.materials.all():
            discount = "-"
            if material.discount_type != 'NONE':
                discount = f"{material.discount_value}{'%' if material.discount_type == 'PERCENTAGE' else 'kg'}"

            row = [
                material.material_type.name,
                material.material_type.get_category_display(),
                material.get_subtype_display(),
                f"${material.material_type.base_price:,.2f}",
                discount,
                f"{material.net_weight:,.2f} kg",
                f"${material.total:,.2f}"
            ]
            material_data.append(row)

        material_data.append([
            "", "", "", "", "TOTAL GENERAL:", 
            f"{total_net_weight:,.2f} kg", 
            f"${total_reception:,.2f}"
        ])

        materials_table = Table(material_data, colWidths=[120, 80, 80, 70, 50, 70, 70])
        materials_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -len(material_data)+1), 0.5, colors.HexColor('#e0e0e0')),
            ('LINEBELOW', (0, -1), (-1, -1), 1, colors.HexColor('#c0392b')),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f8f9fa')),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.HexColor('#c0392b')),
            ('SPAN', (1, -1), (4, -1)),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#f8f9fa')]),
        ]))
        elements.append(materials_table)
        elements.append(Spacer(1, 36))

        # FIRMAS
        elements.append(HRFlowable(width="100%", thickness=1, lineCap='round', color=colors.HexColor('#3498db'), spaceAfter=12))

        signatures = Table([
            ["", ""],["", ""],["", ""],
            ["_________________________", "_________________________"],
            ["Firma del Cliente", "Firma del Responsable"],
            ["", ""],
            ["Nombre: ___________________", "Nombre: ___________________"],
            ["C.I.: ____________________", "C.I.: ____________________"]
        ], colWidths=[250, 250])

        signatures.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LINEABOVE', (0, 1), (0, 1), 1, colors.black),
            ('LINEABOVE', (1, 1), (1, 1), 1, colors.black),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#7f8c8d')),
        ]))
        elements.append(signatures)

        # Nota final
        nota = Paragraph(
            "Documento generado automáticamente. Favor verificar todos los datos al recibir.",
            ParagraphStyle('Nota', parent=styles['Normal'], fontSize=8, alignment=TA_CENTER, textColor=colors.HexColor('#95a5a6'), spaceBefore=24)
        )
        elements.append(nota)

        doc.build(elements, onFirstPage=self.add_page_number, onLaterPages=self.add_page_number)
        return response

    def add_page_number(self, canvas, doc):
        page_num = canvas.getPageNumber()
        text = f"Página {page_num}"
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.HexColor('#95a5a6'))
        canvas.drawRightString(doc.width + doc.rightMargin - 20, 20, text)

















