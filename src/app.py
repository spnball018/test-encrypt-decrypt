from flask import Flask
from api.ingress import ingress_bp

def create_app():
    app = Flask(__name__)
    
    # Register Blueprints
    app.register_blueprint(ingress_bp, url_prefix='/api/v1')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000)
