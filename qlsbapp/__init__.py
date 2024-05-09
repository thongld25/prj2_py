from flask import Flask
from flask_sqlalchemy import SQLAlchemy
# import models
from flask_login import LoginManager
import cloudinary


app = Flask(__name__)
app.secret_key = '@&#&@$GGshfj,jsfbjksdjbfddscv'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:123456@localhost/test'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['PAGE_SIZE'] = 4


db = SQLAlchemy()

db.init_app(app)

cloudinary.config(
    cloud_name = 'divyvvdpl',
    api_key = '375672619841926',
    api_secret = '2dNXMsWLguA01xHScq-8STaWmfo'
)

login_manager = LoginManager()

login_manager.init_app(app)