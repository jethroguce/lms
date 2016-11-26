
import sys

from flask import Flask, render_template, url_for, request, redirect
from flask_restful import Api
from flask_login import LoginManager, logout_user
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView


from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine

app = Flask(__name__, static_url_path='')

app.config.from_object('config')

api = Api(app)
login_manager = LoginManager(app)

conn_str = "mysql+pymysql://{0}:{1}@{2}/{3}".format(
    app.config['DB_USER'],
    app.config['DB_PASSWORD'],
    app.config['DB_SERVER'],
    app.config['DB_SCHEMA'])
print(conn_str)

engine = create_engine(conn_str,
                       connect_args={'connect_timeout': 3},
                       pool_recycle=3600,
                       pool_size=20,
                       max_overflow=20,
                       pool_timeout=5)

try:
    connection = engine.connect()
except:
    print("DB connection failure")
    sys.exit(1)

Session = scoped_session(sessionmaker(bind=engine))

Base = declarative_base()

from .model import *


@app.route('/')
def index():
    db = Session()
    departments = db.query(Department).limit(10).all()
    books = []
    return render_template('index.html',
                            departments=departments,
                            books=books)


@app.route('/login')
def login():
    return 'Lost'


def init_db(db_engine, connection):
    tables = Base.__subclasses__()

    missingtable = False

    for t in tables:
        if db_engine.dialect.has_table(connection, t.__tablename__) is False:
            print('Missing Table')
            missingtable = True
            break

    if missingtable is True:
        print('Creating Table')
        Base.metadata.create_all(db_engine)

init_db(engine, connection)


admin = Admin(app, name='LMS backend', template_mode='bootstrap3')
admin_db_session = Session()

admin.add_view(ModelView(Department, admin_db_session))
admin.add_view(ModelView(Author, admin_db_session))
admin.add_view(ModelView(Book, admin_db_session))
admin.add_view(ModelView(BookContent, admin_db_session))
admin.add_view(ModelView(BookAuthor, admin_db_session))
