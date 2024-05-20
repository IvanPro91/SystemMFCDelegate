from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_restless import APIManager
from flask_scheduler import Scheduler


database = SQLAlchemy()
marshmallow = Marshmallow()
migrate = Migrate()
loginManager = LoginManager()
api_manager = APIManager()
app_Scheduler = Scheduler()
#<script src="https://cdn.socket.io/4.6.0/socket.io.min.js" integrity="sha384-c79GN5VsunZvi+Q/WObgk2in0CbZsHnjEqvFxC5DxHn9lTfNce2WW6h2pH6u/kF+" crossorigin="anonymous"></script>