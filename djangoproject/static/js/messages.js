document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.message-alert').forEach(function(message) {
        setTimeout(function() {
            message.classList.add('fade-out');
            setTimeout(function() {
                message.remove();
                var container = document.querySelector('.message-container');
                if(container && container.children.length === 0) {
                    container.remove();
                }
            }, 500);
    });
});