
from flask import Flask
from controllers.ecuaciones_controller import ecuaciones_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tu_clave_secreta_aqui'

# Registrar blueprints (controladores) los cuales manejan las rutas
app.register_blueprint(ecuaciones_bp)

if __name__ == '__main__':
    app.run(debug=True)