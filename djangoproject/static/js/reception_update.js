document.addEventListener('DOMContentLoaded', function() {
    console.log('Inicializando formulario de edición de recepción');
    
    // Contadores basados en los datos existentes
    let materialCounter = 0;
    const operationCounters = {};
    
    // Elementos del DOM
    const addMaterialBtn = document.getElementById('add-material-btn');
    const materialsContainer = document.getElementById('materials-container');
    const receptionForm = document.getElementById('reception-form');
    
    // Templates
    const materialTemplate = document.getElementById('material-template');
    const operationTemplate = document.getElementById('operation-template');

    // Función para cargar materiales existentes
    function loadExistingMaterials() {
        const receptionData = JSON.parse(document.getElementById('reception-data').textContent);
        
        receptionData.materials.forEach(material => {
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
            const insertedMaterial = materialsContainer.lastElementChild;
            
            // Rellenar datos del material
            const typeSelect = insertedMaterial.querySelector('.material-type');
            typeSelect.value = material.material_type.id;
            
            const subtypeSelect = insertedMaterial.querySelector('select[name$="[subtype]"]');
            subtypeSelect.value = material.subtype;
            
            const discountType = insertedMaterial.querySelector('select[name$="[discount_type]"]');
            discountType.value = material.discount_type;
            
            const discountValue = insertedMaterial.querySelector('input[name$="[discount_value]"]');
            discountValue.value = material.discount_value;
            
            // Añadir operaciones existentes
            material.operations.forEach(operation => {
                addOperation(materialIndex, operation);
            });
            
            // Configurar eventos para el nuevo material
            setupMaterialEvents(materialIndex);
        });
    }
    
    // Función para añadir operación (con datos existentes si se proporcionan)
    function addOperation(materialIndex, operationData = null) {
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
        const operationRow = operationsBody.lastElementChild;
        
        // Rellenar datos de operación si existen
        if (operationData) {
            operationRow.querySelector('.gross').value = operationData.gross_weight;
            operationRow.querySelector('.tare').value = operationData.tare_weight;
            calculateOperationNetWeight(operationRow.querySelector('.gross'));
        }
        
        // Configurar eventos para la nueva operación
        setupOperationEvents(materialIndex, opIndex);
    }
    
    // Configurar eventos para un material (igual que en reception_create.js)
    function setupMaterialEvents(materialIndex) {
        const materialElement = document.querySelector('[data-material-index="${materialIndex}"]');
        
        materialElement.querySelector('.add-operation').addEventListener('click', function() {
            addOperation(materialIndex);
        });
        
        materialElement.querySelector('.remove-material').addEventListener('click', function() {
            materialElement.remove();
            calculateTotals();
        });
        
        materialElement.querySelector('.discount-type').addEventListener('change', calculateTotals);
        materialElement.querySelector('.discount-value').addEventListener('input', calculateTotals);
        materialElement.querySelector('.material-type').addEventListener('change', calculateTotals);
    }
    
    // Configurar eventos para una operación (igual que en reception_create.js)
    function setupOperationEvents(materialIndex, opIndex) {
        const operationRow = document.querySelector('[data-material-index="${materialIndex}"] .operation-row[data-op-index="${opIndex}"]');
        
        operationRow.querySelector('.gross').addEventListener('input', function() {
            calculateOperationNetWeight(this);
            calculateTotals();
        });
        
        operationRow.querySelector('.tare').addEventListener('input', function() {
            calculateOperationNetWeight(this);
            calculateTotals();
        });
        
        operationRow.querySelector('.remove-operation').addEventListener('click', function() {
            operationRow.remove();
            calculateTotals();
        });
    }
    
    // Resto de funciones (calculateOperationNetWeight, calculateTotals, etc.) igual que en reception_create.js
    
    // Inicialización
    if (document.getElementById('reception-data')) {
        loadExistingMaterials();
    } else {
        addMaterialBtn.addEventListener('click', addMaterial);
        addMaterial(); // Añadir primer material si no hay datos existentes
    }
});