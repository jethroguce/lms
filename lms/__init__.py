
import os
import os.path as op
import sys
import time

from flask import Flask, render_template, url_for, request, redirect
from flask_restful import Api
from flask_login import LoginManager, current_user, login_user, logout_user

from wtforms import form, fields, validators

from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_admin import helpers, expose
from flask_admin import form as admin_form

from werkzeug.security import generate_password_hash, check_password_hash

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine

app = Flask(__name__, static_url_path='')

app.config.from_object('config')

api = Api(app)
login_manager = LoginManager(app)

# Create directory for file fields to use
static_path = op.join(op.dirname(__file__), 'static', 'upload')
file_path = op.join(op.dirname(__file__), 'static', 'upload')
try:
    os.mkdir(file_path)
except OSError:
    pass

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

Session = sessionmaker(bind=engine)

Base = declarative_base()


from .model import *


# Create user loader function
@login_manager.user_loader
def load_user(user_id):
    db = Session()
    return db.query(User).get(user_id)


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


# Define login and registration forms (for flask-login)
class LoginForm(form.Form):
    login = fields.StringField(validators=[validators.required()])
    password = fields.PasswordField(validators=[validators.required()])

    def validate_login(self, field):
        user = self.get_user()

        if user is None:
            raise validators.ValidationError('Invalid user')

        # we're comparing the plaintext pw with the the hash from the db
        if not check_password_hash(user.password, self.password.data):
        # to compare plain text passwords use
        # if user.password != self.password.data:
            raise validators.ValidationError('Invalid password')

    def get_user(self):
        db = Session()
        return db.query(User).filter_by(login=self.login.data).first()


class RegistrationForm(form.Form):
    login = fields.StringField(validators=[validators.required()])
    email = fields.StringField()
    password = fields.PasswordField(validators=[validators.required()])

    def validate_login(self, field):
        db = Session()
        if db.query(User).filter_by(login=self.login.data).count() > 0:
            raise validators.ValidationError('Duplicate username')



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

# Create customized model view class
class MyModelView(ModelView):

    def is_accessible(self):
        return current_user.is_authenticated


# Create customized index view class that handles login & registration
class MyAdminIndexView(AdminIndexView):

    @expose('/')
    def index(self):
        if not current_user.is_authenticated:
            return redirect(url_for('.login_view'))
        return super(MyAdminIndexView, self).index()

    @expose('/login/', methods=('GET', 'POST'))
    def login_view(self):
        # handle user login
        form = LoginForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = form.get_user()
            login_user(user)

        if current_user.is_authenticated:
            return redirect(url_for('.index'))
        link = '<p>Don\'t have an account? <a href="' + url_for('.register_view') + '">Click here to register.</a></p>'
        self._template_args['form'] = form
        self._template_args['link'] = link
        return super(MyAdminIndexView, self).index()

    @expose('/register/', methods=('GET', 'POST'))
    def register_view(self):
        form = RegistrationForm(request.form)
        if helpers.validate_form_on_submit(form):
            session = Session()
            user = User()

            form.populate_obj(user)
            # we hash the users password to avoid saving it as plaintext in the db,
            # remove to use plain text:
            user.password = generate_password_hash(form.password.data, 'pbkdf2:sha256')

            session.add(user)
            session.commit()

            login_user(user)
            return redirect(url_for('.index'))
        link = '<p>Already have an account? <a href="' + url_for('.login_view') + '">Click here to log in.</a></p>'
        self._template_args['form'] = form
        self._template_args['link'] = link
        return super(MyAdminIndexView, self).index()

    @expose('/logout/')
    def logout_view(self):
        logout_user()
        return redirect(url_for('.index'))


def prefix_name(obj, file_data):
    ts = time.time()
    parts = op.splitext(file_data.filename)
    return '{}{}'.format(ts, parts[1])

# Administrative views
class FileView(MyModelView):
    # Override form field to use Flask-Admin FileUploadField
    form_overrides = {
        'path': admin_form.FileUploadField,
        'cover': admin_form.ImageUploadField,
    }

    # Pass additional parameters to 'path' to FileUploadField constructor
    form_args = {
        'path': {
            'label': 'File',
            'base_path': file_path,
            'relative_path': 'upload/',
            'allow_overwrite': False,
            'namegen': prefix_name
        },
        'cover': {
            'label': 'Cover',
            'base_path': file_path,
            'relative_path': 'upload/',
            'url_relative_path': 'upload/',
            'allow_overwrite': False,
            'namegen': prefix_name,
            'thumbnail_size': (150, 200, False)
        }
    }



admin = Admin(app, name='SLSU Admin', index_view=MyAdminIndexView(),
                base_template='my_master.html',
                template_mode='bootstrap3')
admin_db_session = Session()

admin.add_view(MyModelView(Department, admin_db_session))
admin.add_view(MyModelView(Author, admin_db_session))
admin.add_view(FileView(Book, admin_db_session))
admin.add_view(MyModelView(BookAuthor, admin_db_session))
