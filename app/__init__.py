#!venv/bin/python

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_redis import FlaskRedis

app = Flask(__name__)
app.config.from_object('config')
lm = LoginManager(app)
lm.login_view = 'login'
db = SQLAlchemy(app)
redis_store = FlaskRedis(app)


from app import views, models,api