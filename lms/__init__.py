
from flask import Flask, render_template, url_for, request, redirect
from flask_restful import Api
from flask_login import LoginManager, logout_user
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView


from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

app = Flask(__name__, static_url_path='')

app.config.from_object('config')

api = Api(app)
login_manager = LoginManager(app)
admin = Admin(app, name='lms', template_mode='bootstrap3')


Base = declarative_base()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login')
def login():
    return 'Lost'

