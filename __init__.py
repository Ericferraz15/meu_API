from flask import Flask, request 
from markupsafe import escape
import secrets  
import os 
from . import db
from .auth import bp
def create_app():
    app = Flask(__name__,instance_relative_config=True)
    app.config.from_mapping(
        API_KEY = secrets.token_hex(),
        BATABASE = os.path.join(app.instance_path, "flash_sqlite"))
        
    app.config.from_mapping(
        SECRET_KEY="dev",  # só exemplo, troque em produção
        DATABASE=os.path.join(app.instance_path, "meu_API.sqlite"), 
    )
        
    try:
        os.makedirs(app.instance_path)
    except OSError:
            pass
        
    @app.route("/hello")
    def hello():
        return 'hello'
    
    db.init_app(app)
    app.register_blueprint(bp)# type: ignore

    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')
    return app