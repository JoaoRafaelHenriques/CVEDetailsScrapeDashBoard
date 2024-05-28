from flask import Flask
import routes
from modules.utils import inicializa
        
def create_app():
    
    app = Flask(__name__)
    app.static_folder = 'static'
    
    with app.app_context():
        inicializa(app)
    
    app.register_blueprint(routes.bp)
    return app

if __name__ == '__main__':
    import sys
    port = 5000  # Porta padrão

    if len(sys.argv) > 1:
        port = int(sys.argv[1])

    app = create_app()
    app.run(host='0.0.0.0', port=port)
    
    
# python3 app.py PORTA
