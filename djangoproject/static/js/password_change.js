document.addEventListener('DOMContentLoaded', function() {
    // Añade clases a los inputs de contraseña
    const passwordInputs = document.querySelectorAll('input[type="password"], input[type="text"].password-input');
    
    passwordInputs.forEach(input => {
        input.classList.add('form-control');
        input.style.paddingRight = '35px'; // Espacio para el icono
    });

    // Configura los toggles de contraseña
    setupPasswordToggles();
    
    // Validación adicional del formulario
    setupFormValidation();
});

function setupPasswordToggles() {
    const toggleButtons = document.querySelectorAll('.password-toggle');
    
    toggleButtons.forEach(button => {
        button.addEventListener('click', function() {
            const inputGroup = this.closest('.password-field-group');
            const passwordInput = inputGroup.querySelector('input');
            const icon = this.querySelector('i');
            
            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                icon.classList.remove('icon-eye');
                icon.classList.add('icon-eye-blocked');
            } else {
                passwordInput.type = 'password';
                icon.classList.remove('icon-eye-blocked');
                icon.classList.add('icon-eye');
            }
        });
    });
}

function setupFormValidation() {
    const form = document.getElementById('passwordChangeForm');
    
    if (form) {
        form.addEventListener('submit', function(event) {
            const newPassword1 = form.querySelector('#id_new_password1').value;
            const newPassword2 = form.querySelector('#id_new_password2').value;
            
            if (newPassword1 !== newPassword2) {
                event.preventDefault();
                showInlineError('Las contraseñas no coinciden', 'id_new_password2');
            }
        });
    }
}

function showInlineError(message, fieldId) {
    // Elimina errores previos
    const existingError = document.querySelector(`#${fieldId}`).nextElementSibling;
    if (existingError && existingError.classList.contains('text-danger')) {
        existingError.remove();
    }
    
    // Crea y muestra el nuevo error
    const errorElement = document.createElement('small');
    errorElement.classList.add('text-danger', 'd-block', 'mt-1');
    errorElement.textContent = message;
    
    const field = document.querySelector(`#${fieldId}`);
    field.parentNode.insertBefore(errorElement, field.nextSibling);
    
    // Enfoca el campo con error
    field.focus();
}