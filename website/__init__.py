from flask import Flask
from .config import Config
from .extensions import *

from .includes.database.database_models import *
from .routes.page_mfc import main_mfc
from .routes.page_auth import auth
from .routes.page_orders import orders
from .routes.page_queue import queue
from .routes.page_settings import settings
from .routes.page_user_org import user_org


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Подключаем маршруты
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(main_mfc, url_prefix='/')
    app.register_blueprint(settings, url_prefix='/')
    app.register_blueprint(orders, url_prefix='/')
    app.register_blueprint(user_org, url_prefix='/')
    app.register_blueprint(queue, url_prefix='/')

    database.init_app(app)
    migrate.init_app(app, database)

    loginManager.login_message = ''
    loginManager.login_view = "auth.user_auth"
    loginManager.init_app(app)
    
    @loginManager.user_loader
    def loadUser(user_id):
        return Users.query.get(int(user_id))

    return app