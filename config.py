
import os

BIND_IP = '127.0.0.1'
BIND_PORT = 8080
DEBUG = True

DB_SERVER = os.environ['DB_SERVER']
DB_USER = os.environ['DB_USER']
DB_PASSWORD = os.environ['DB_PASSWORD']
DB_SCHEMA = os.environ['DB_SCHEMA']

SECRET_KEY = 'saof12341jhada72341'
