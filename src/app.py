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
    create_app()
    
    
# flask run