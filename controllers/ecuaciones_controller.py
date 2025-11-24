from flask import Blueprint, render_template, request, jsonify
from services.resolver_ecuaciones import resolver_ecuacion_exacta
from models.ecuaciones import EcuacionDiferencial

# Definir el blueprint para las ecuaciones diferenciales el cual manejará las rutas relacionadas
ecuaciones_bp = Blueprint('ecuaciones', __name__)
# Ruta para la página principal
@ecuaciones_bp.route('/')
def index():
    return render_template('index.html')
# Ruta para resolver la ecuación diferencial la cual recibe datos del formulario
@ecuaciones_bp.route('/resolver', methods=['POST'])
def resolver():
    try:
        # Recibir datos del formulario que se envía por POST desde la página web en index.html
        datos = request.form
        
        # Crear modelo de ecuación
        ecuacion = EcuacionDiferencial(datos)
        
        # Resolver usando el servicio
        resultado = resolver_ecuacion_exacta(ecuacion)
        
        
        # Renderizar resultados en una nueva página
        return render_template('resultados.html', resultado=resultado)
    except Exception as e:
        return render_template('index.html', error=str(e))