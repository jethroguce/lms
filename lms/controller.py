from flask_restful import Resource, reqparse
from .model import Book


class BookHandler(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('title', type=str)
        self.reqparse.add_argument('code', type=str)
        self.reqparse.add_argument('description', type=str)

    def get(self):
        pass

    def post(self):
        pass
