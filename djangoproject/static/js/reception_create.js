document.addEventListener('DOMContentLoaded', function() {
    console.log('Inicializando formulario de recepción');

    // Contadores
    let materialCounter = 0;
    const operationCounters = {};

    // Elementos del DOM
    const addMaterialBtn = document.getElementById('add-material-btn');
    const materialsContainer = document.getElementById('materials-container');
    const receptionForm = document.getElementById('reception-form');

    // Templates
    const materialTemplate = document.getElementById('material-template');
    const operationTemplate = document.getElementById('operation-template');

    // Verificar si estamos editando
    const isEditing = document.querySelector('input[name="editing"]') !== null;
    console.log('isEditing:', isEditing);

    // Función para añadir material
    function addMaterial() {
        const materialIndex = materialCounter++;
        operationCounters[materialIndex] = 0;
        console.log(`Añadiendo material con índice: ${materialIndex}`);

        // Clonar template y reemplazar índices
        const newMaterial = materialTemplate.content.cloneNode(true);
        const materialElement = newMaterial.querySelector('.material-item');
        materialElement.dataset.materialIndex = materialIndex;

        // Actualizar todos los names con el índice correcto
        const materialHtml = materialElement.outerHTML
            .replace(/{index}/g, materialIndex)
            .replace(/{materialIndex}/g, materialIndex);

        // Insertar en el DOM
        materialsContainer.insertAdjacentHTML('beforeend', materialHtml);
        console.log(`Material insertado en el DOM con índice: ${materialIndex}`);

        // Añadir primera operación
        addOperation(materialIndex);

        // Configurar eventos para el nuevo material
        setupMaterialEvents(materialIndex);
    }

    // Función para añadir operación
    function addOperation(materialIndex) {
        const opIndex = operationCounters[materialIndex]++;
        console.log(`Añadiendo operación ${opIndex} al material ${materialIndex}`);
        const materialElement = document.querySelector(`[data-material-index="${materialIndex}"]`);
        const operationsBody = materialElement.querySelector('.operations-body');

        // Clonar template y reemplazar índices
        const newOperation = operationTemplate.content.cloneNode(true);
        const operationHtml = newOperation.querySelector('.operation-row').outerHTML
            .replace(/{materialIndex}/g, materialIndex)
            .replace(/{opIndex}/g, opIndex)
            .replace(/{opNumber}/g, opIndex + 1);

        operationsBody.insertAdjacentHTML('beforeend', operationHtml);
        console.log(`Operación insertada en el DOM: material ${materialIndex}, operación ${opIndex}`);

        // Configurar eventos para la nueva operación
        setupOperationEvents(materialIndex, opIndex);
    }

    // Configurar eventos para un material
    function setupMaterialEvents(materialIndex) {
        const materialElement = document.querySelector(`[data-material-index="${materialIndex}"]`);
        console.log(`Configurando eventos para material ${materialIndex}`);

        // Evento para añadir operación
        materialElement.querySelector('.add-operation').addEventListener('click', function() {
            console.log(`Click en añadir operación para material ${materialIndex}`);
            addOperation(materialIndex);
        });

        // Evento para eliminar material
        materialElement.querySelector('.remove-material').addEventListener('click', function() {
            console.log(`Eliminando material ${materialIndex}`);
            materialElement.remove();
            calculateTotals();
        });

        // Eventos para cambios en descuentos
        materialElement.querySelector('.discount-type').addEventListener('change', function() {
            console.log(`Cambio en tipo de descuento en material ${materialIndex}`);
            calculateTotals();
        });
        materialElement.querySelector('.discount-value').addEventListener('input', function() {
            console.log(`Cambio en valor de descuento en material ${materialIndex}`);
            calculateTotals();
        });
        materialElement.querySelector('.material-type').addEventListener('change', function() {
            console.log(`Cambio en tipo de material en material ${materialIndex}`);
            calculateTotals();
        });
    }

    // Configurar eventos para una operación
    function setupOperationEvents(materialIndex, opIndex) {
        const operationRow = document.querySelector(`[data-material-index="${materialIndex}"] .operation-row[data-op-index="${opIndex}"]`);
        console.log(`Configurando eventos para operación ${opIndex} de material ${materialIndex}`);

        // Eventos para cálculo de peso neto
        operationRow.querySelector('.gross').addEventListener('input', function() {
            console.log(`Input bruto en operación ${opIndex} de material ${materialIndex}`);
            calculateOperationNetWeight(this);
            calculateTotals();
        });

        operationRow.querySelector('.tare').addEventListener('input', function() {
            console.log(`Input tara en operación ${opIndex} de material ${materialIndex}`);
            calculateOperationNetWeight(this);
            calculateTotals();
        });

        // Evento para eliminar operación
        operationRow.querySelector('.remove-operation').addEventListener('click', function() {
            console.log(`Eliminando operación ${opIndex} de material ${materialIndex}`);
            operationRow.remove();
            calculateTotals();
        });
    }

    // Calcular peso neto de una operación
    function calculateOperationNetWeight(inputElement) {
        const row = inputElement.closest('.operation-row');
        const gross = parseFloat(row.querySelector('.gross').value) || 0;
        const tare = parseFloat(row.querySelector('.tare').value) || 0;
        const net = gross - tare;
        console.log(`Calculando peso neto: bruto=${gross}, tara=${tare}, neto=${net}`);

        row.querySelector('.net-weight').textContent = net.toFixed(2);

        // Marcar como inválido si net es negativo
        if (net <= 0) {
            row.classList.add('invalid-operation');
            console.log('Operación inválida: peso neto <= 0');
        } else {
            row.classList.remove('invalid-operation');
        }
    }

    // Calcular totales generales
    function calculateTotals() {
        let totalNetWeight = 0;
        let totalValue = 0;
        console.log('Calculando totales generales');

        document.querySelectorAll('.material-item').forEach(materialElement => {
            const materialIndex = materialElement.dataset.materialIndex;
            const materialTypeSelect = materialElement.querySelector('.material-type');
            const price = parseFloat(materialTypeSelect.selectedOptions[0]?.dataset.price) || 0;
            const discountType = materialElement.querySelector('.discount-type').value;
            const discountValue = parseFloat(materialElement.querySelector('.discount-value').value) || 0;

            // Calcular subtotal del material
            let subtotal = 0;
            materialElement.querySelectorAll('.operation-row').forEach(op => {
                subtotal += parseFloat(op.querySelector('.net-weight').textContent) || 0;
            });

            // Aplicar descuento
            let discount = 0;
            if (discountType === 'ABSOLUTE') {
                discount = discountValue;
            } else if (discountType === 'PERCENTAGE') {
                discount = subtotal * (discountValue / 100);
            }

            const netWeight = subtotal - discount;
            const materialValue = netWeight * price;

            // Actualizar totales del material
            materialElement.querySelector('.material-subtotal').textContent = subtotal.toFixed(2);
            materialElement.querySelector('.material-discount').textContent = discount.toFixed(2);
            materialElement.querySelector('.material-total').textContent = `${netWeight.toFixed(2)} kg ($${materialValue.toFixed(2)})`;

            // Acumular totales generales
            totalNetWeight += netWeight;
            totalValue += materialValue;

            console.log(`Material ${materialIndex}: subtotal=${subtotal}, descuento=${discount}, neto=${netWeight}, valor=${materialValue}`);
        });

        // Actualizar totales generales
        document.getElementById('total-net-weight').textContent = `${totalNetWeight.toFixed(2)} kg`;
        document.getElementById('total-reception').textContent = `$${totalValue.toFixed(2)}`;
        console.log(`Totales generales: peso neto=${totalNetWeight}, valor total=${totalValue}`);
    }

    // Validación del formulario
    receptionForm.addEventListener('submit', function(e) {
        let isValid = true;
        console.log('Validando formulario de recepción');

        // Validar cliente
        if (!document.getElementById('client-select').value) {
            isValid = false;
            alert('Seleccione un cliente');
            console.log('Validación fallida: cliente no seleccionado');
        }

        // Validar materiales
        const materialItems = document.querySelectorAll('.material-item');
        if (materialItems.length === 0) {
            isValid = false;
            alert('Debe añadir al menos un material');
            console.log('Validación fallida: no hay materiales');
        }

        // Validar cada material
        materialItems.forEach(material => {
            if (!material.querySelector('.material-type').value) {
                isValid = false;
                alert('Seleccione el tipo de material para todos los items');
                console.log('Validación fallida: tipo de material no seleccionado');
            }

            if (material.querySelectorAll('.invalid-operation').length > 0) {
                isValid = false;
                alert('Hay operaciones con peso neto inválido (bruto ≤ tara)');
                console.log('Validación fallida: operaciones inválidas');
            }
        });

        if (!isValid) {
            e.preventDefault();
            console.log('Formulario inválido, se previene el envío');
        } else {
            console.log('Formulario válido, enviando...');
        }
    });

function loadExistingReception() {
    if (!isEditing) return;
    console.log('Cargando datos de recepción existente');

    try {
        const receptionDataElement = document.getElementById('reception-data');
        if (!receptionDataElement) {
            console.error('Elemento reception-data no encontrado');
            addMaterial(); // Fallback
            return;
        }

        const receptionData = JSON.parse(receptionDataElement.textContent);
        console.log('Datos completos de recepción:', receptionData);

        // Limpiar contadores
        materialCounter = 0;
        Object.keys(operationCounters).forEach(key => delete operationCounters[key]);

        // Limpiar contenedor (opcional, dependiendo de tu flujo)
        materialsContainer.innerHTML = '';

        // Procesar cada material
        receptionData.forEach((material, materialIdx) => {
            const materialIndex = materialCounter++;
            operationCounters[materialIndex] = 0;
            console.log(`Procesando material ${materialIdx} con índice ${materialIndex}`);

            // Clonar template CORRECTAMENTE
            const materialClone = document.importNode(materialTemplate.content, true);
            const materialElement = materialClone.querySelector('.material-item');
            
            // Actualizar atributos data
            materialElement.dataset.materialIndex = materialIndex;
            
            // Actualizar names e IDs en TODOS los elementos
            const allElements = materialElement.querySelectorAll('[name], [id]');
            allElements.forEach(el => {
                if (el.name) el.name = el.name.replace(/{index}/g, materialIndex)
                                             .replace(/{materialIndex}/g, materialIndex);
                if (el.id) el.id = el.id.replace(/{index}/g, materialIndex)
                                       .replace(/{materialIndex}/g, materialIndex);
            });

            // Insertar en el DOM
            materialsContainer.appendChild(materialClone);
            
            // Rellenar datos del material
            const typeSelect = materialElement.querySelector('.material-type');
            if (typeSelect) {
                typeSelect.value = material.material_type?.id || '';
                // Disparar evento change para actualizar precios
                typeSelect.dispatchEvent(new Event('change'));
            }

            materialElement.querySelector('select[name$="[subtype]"]').value = material.subtype || 'LIMPIO';
            materialElement.querySelector('.discount-type').value = material.discount_type || 'NONE';
            materialElement.querySelector('.discount-value').value = material.discount_value || '0.00';

            // Procesar operaciones
            const operationsBody = materialElement.querySelector('.operations-body');
            if (material.operations && material.operations.length > 0) {
                material.operations.forEach((op, opIdx) => {
                    const opIndex = operationCounters[materialIndex]++;
                    console.log(`Añadiendo operación ${opIndex} al material ${materialIndex}`);

                    const operationClone = document.importNode(operationTemplate.content, true);
                    const opRow = operationClone.querySelector('.operation-row');
                    
                    // Actualizar atributos data
                    opRow.dataset.opIndex = opIndex;
                    
                    // Actualizar contenido
                    opRow.querySelector('.op-number').textContent = opIndex + 1;
                    
                    // Actualizar names
                    const opInputs = opRow.querySelectorAll('[name]');
                    opInputs.forEach(input => {
                        input.name = input.name.replace(/{materialIndex}/g, materialIndex)
                                             .replace(/{opIndex}/g, opIndex);
                    });

                    // Rellenar valores
                    opRow.querySelector('.gross').value = op.gross_weight || '0.00';
                    opRow.querySelector('.tare').value = op.tare_weight || '0.00';
                    
                    // Insertar y calcular
                    operationsBody.appendChild(operationClone);
                    calculateOperationNetWeight(opRow.querySelector('.gross'));
                    
                    // Configurar eventos
                    setupOperationEvents(materialIndex, opIndex);
                });
            } else {
                console.log(`Material ${materialIndex} sin operaciones, añadiendo una vacía`);
                addOperation(materialIndex);
            }

            // Configurar eventos del material
            setupMaterialEvents(materialIndex);
        });

        // Calcular totales finales
        calculateTotals();

    } catch (error) {
        console.error('Error al cargar recepción:', error);
        // Fallback: añadir material vacío
        addMaterial();
    }
}

    // Inicialización
    addMaterialBtn.addEventListener('click', function() {
        console.log('Click en botón añadir material');
        addMaterial();
    });

    if (isEditing) {
        loadExistingReception();
        console.log('Datos recibidos:', JSON.parse(document.getElementById('reception-data').textContent));
    } else {
        addMaterial(); // Añadir primer material al cargar solo en creación
    }
});