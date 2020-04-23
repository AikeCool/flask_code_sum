from flask import Flask
from .views.reg.login import lg
from .views.reg.logout import lt
from .views.index import blue_index
from .views.detail import blue_detail
import settings

def run_app():
    app = Flask(__name__)
    app.config.from_object("settings.Dev")
    # app.secret_key = "aike"


    app.register_blueprint(lg)
    app.register_blueprint(lt)
    app.register_blueprint(blue_index)
    app.register_blueprint(blue_detail)
    return app
