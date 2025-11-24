document.addEventListener('DOMContentLoaded', function() {
    // Funcionalidad de toggle para mostrar/ocultar teclados
    const botonesToggle = document.querySelectorAll('.btn-toggle-teclado');
    
    botonesToggle.forEach(boton => {
        boton.addEventListener('click', function() {
            const targetId = this.getAttribute('data-target');
            const teclado = document.getElementById('teclado' + targetId.replace('input', ''));
            
            // Toggle clase show
            teclado.classList.toggle('show');
            this.classList.toggle('active');
            
            // Cambiar texto del botón
            if (teclado.classList.contains('show')) {
                this.textContent = '⌨️ Ocultar Teclado';
            } else {
                this.textContent = '⌨️ Desplegar Teclado';
            }
        });
    });
    
    // Funcionalidad de los botones del teclado
    const teclados = document.querySelectorAll('.teclado-matematico');
    
    teclados.forEach(teclado => {
        const targetId = teclado.getAttribute('data-target');
        const input = document.getElementById(targetId);
        
        teclado.querySelectorAll('.btn-tecla').forEach(boton => {
            boton.addEventListener('click', function() {
                const valor = this.textContent;
                const cursorPos = input.selectionStart;
                const textoActual = input.value;
                
                // Insertar el valor en la posición del cursor
                const nuevoTexto = textoActual.substring(0, cursorPos) + 
                                   valor + 
                                   textoActual.substring(cursorPos);
                
                input.value = nuevoTexto;
                
                // Mover el cursor después del texto insertado
                const nuevaPosicion = cursorPos + valor.length;
                input.setSelectionRange(nuevaPosicion, nuevaPosicion);
                input.focus();
            });
        });
    });
});