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

    // Función para añadir material
    function addMaterial() {
        const materialIndex = materialCounter++;
        operationCounters[materialIndex] = 0;
        
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
        
        // Añadir primera operación
        addOperation(materialIndex);
        
        // Configurar eventos para el nuevo material
        setupMaterialEvents(materialIndex);
    }
    
    // Función para añadir operación
    function addOperation(materialIndex) {
        const opIndex = operationCounters[materialIndex]++;
        const materialElement = document.querySelector(`[data-material-index="${materialIndex}"]`);
        const operationsBody = materialElement.querySelector('.operations-body');
        
        // Clonar template y reemplazar índices
        const newOperation = operationTemplate.content.cloneNode(true);
        const operationHtml = newOperation.querySelector('.operation-row').outerHTML
            .replace(/{materialIndex}/g, materialIndex)
            .replace(/{opIndex}/g, opIndex)
            .replace(/{opNumber}/g, opIndex + 1);
        
        operationsBody.insertAdjacentHTML('beforeend', operationHtml);
        
        // Configurar eventos para la nueva operación
        setupOperationEvents(materialIndex, opIndex);
    }
    
    // Configurar eventos para un material
    function setupMaterialEvents(materialIndex) {
        const materialElement = document.querySelector(`[data-material-index="${materialIndex}"]`);
        
        // Evento para añadir operación
        materialElement.querySelector('.add-operation').addEventListener('click', function() {
            addOperation(materialIndex);
        });
        
        // Evento para eliminar material
        materialElement.querySelector('.remove-material').addEventListener('click', function() {
            materialElement.remove();
            calculateTotals();
        });
        
        // Eventos para cambios en descuentos
        materialElement.querySelector('.discount-type').addEventListener('change', calculateTotals);
        materialElement.querySelector('.discount-value').addEventListener('input', calculateTotals);
        materialElement.querySelector('.material-type').addEventListener('change', calculateTotals);
    }
    
    // Configurar eventos para una operación
    function setupOperationEvents(materialIndex, opIndex) {
        const operationRow = document.querySelector(`[data-material-index="${materialIndex}"] .operation-row[data-op-index="${opIndex}"]`);
        
        // Eventos para cálculo de peso neto
        operationRow.querySelector('.gross').addEventListener('input', function() {
            calculateOperationNetWeight(this);
            calculateTotals();
        });
        
        operationRow.querySelector('.tare').addEventListener('input', function() {
            calculateOperationNetWeight(this);
            calculateTotals();
        });
        
        // Evento para eliminar operación
        operationRow.querySelector('.remove-operation').addEventListener('click', function() {
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
        
        row.querySelector('.net-weight').textContent = net.toFixed(2);
        
        // Marcar como inválido si net es negativo
        if (net <= 0) {
            row.classList.add('invalid-operation');
        } else {
            row.classList.remove('invalid-operation');
        }
    }
    
    // Calcular totales generales
    function calculateTotals() {
        let totalNetWeight = 0;
        let totalValue = 0;
        
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
        });
        
        // Actualizar totales generales
        document.getElementById('total-net-weight').textContent = `${totalNetWeight.toFixed(2)} kg`;
        document.getElementById('total-reception').textContent = `$${totalValue.toFixed(2)}`;
    }
    
    // Validación del formulario
    receptionForm.addEventListener('submit', function(e) {
        let isValid = true;
        
        // Validar cliente
        if (!document.getElementById('client-select').value) {
            isValid = false;
            alert('Seleccione un cliente');
        }
        
        // Validar materiales
        const materialItems = document.querySelectorAll('.material-item');
        if (materialItems.length === 0) {
            isValid = false;
            alert('Debe añadir al menos un material');
        }
        
        // Validar cada material
        materialItems.forEach(material => {
            if (!material.querySelector('.material-type').value) {
                isValid = false;
                alert('Seleccione el tipo de material para todos los items');
            }
            
            if (material.querySelectorAll('.invalid-operation').length > 0) {
                isValid = false;
                alert('Hay operaciones con peso neto inválido (bruto ≤ tara)');
            }
        });
        
        if (!isValid) {
            e.preventDefault();
        }
    });
    
    // Inicialización
    addMaterialBtn.addEventListener('click', addMaterial);
    addMaterial(); // Añadir primer material al cargar
});