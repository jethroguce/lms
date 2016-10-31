
from flask import Flask, render_template, url_for, request, redirect

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

app = Flask(__name__, static_url_path='')

app.config.from_object('config')


Base = declarative_base()


@app.route('/')
def index():
    return 'Hello World'
