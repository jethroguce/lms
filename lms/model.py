
import os
import os.path as op
import datetime

from decimal import Decimal

from sqlalchemy.orm import relationship
from sqlalchemy import Integer, String, Boolean, DateTime, TEXT, LargeBinary
from sqlalchemy import Column, Sequence, Index, ForeignKey, func
from sqlalchemy.event import listens_for

from lms import Base, file_path


class GenericBase(object):
    id = Column(Integer)

    def as_dict(self):
        return ({c.name: getattr(self, c.name) for c in self.__table__.columns})

    def toJSONExcept(self, except_fields=[]):
        retval = {}
        ad = self.as_dict()
        #print(ad)
        for k in ad:
            #print (k)
            if k in except_fields:
                continue

            #print (k, type(ad[k]))
            if type(ad[k]) is datetime.datetime:
                ad[k] = ad[k].isoformat() + 'Z'
            elif type(ad[k]) is Decimal:
                ad[k] = float(ad[k])

            retval[k] = ad[k]

        return retval


class Department(GenericBase, Base):
    __tablename__ = 'department'
    GenericBase.id = Column(Integer, Sequence(__tablename__ + '_id_seq'), primary_key=True)
    name = Column(String(100), nullable=False)
    books = relationship('Book')

    createdate = Column(DateTime, default=func.now())
    lastupdate = Column(DateTime, default=func.now(), onupdate=func.now())
    active = Column(Boolean, default=True)

    def __repr__(self):
        return self.name


class Book(GenericBase, Base):
    __tablename__ = 'book'
    GenericBase.id = Column(Integer, Sequence(__tablename__ + '_id_seq'), primary_key=True)
    title = Column(String(300), nullable=False)
    code = Column(String(50), nullable=False)
    description = Column(TEXT)

    department00_id = Column(Integer, ForeignKey(Department.__tablename__ + '.id'))
    department = relationship('Department', foreign_keys=[department00_id])
    year = Column(Integer)
    cover = Column(String(128))
    authors = relationship('BookAuthor')

    createdate = Column(DateTime, default=func.now())
    lastupdate = Column(DateTime, default=func.now(), onupdate=func.now())
    active = Column(Boolean, default=True)

    def __repr__(self):
        return self.title


class File(GenericBase, Base):
    __tablename__ = 'file'
    GenericBase.id = Column(Integer, Sequence(__tablename__ + '_id_seq'), primary_key=True)
    book00_id = Column(Integer, ForeignKey(Book.__tablename__ + '.id'))
    book = relationship('Book', foreign_keys=[book00_id])

    file_type = Column(String(20))
    path = Column(String(128))

    createdate = Column(DateTime, default=func.now())
    lastupdate = Column(DateTime, default=func.now(), onupdate=func.now())
    active = Column(Boolean, default=True)


class Author(GenericBase, Base):
    __tablename__ = 'author'
    GenericBase.id = Column(Integer, Sequence(__tablename__ + '_id_seq'), primary_key=True)
    name = Column(String(200), nullable=False)

    books = relationship('BookAuthor')

    createdate = Column(DateTime, default=func.now())
    lastupdate = Column(DateTime, default=func.now(), onupdate=func.now())
    active = Column(Boolean, default=True)

    def __repr__(self):
        return self.name


class BookAuthor(GenericBase, Base):
    __tablename__ = 'book_author'
    GenericBase.id = Column(Integer, Sequence(__tablename__ + '_id_seq'), primary_key=True)

    book00_id = Column(Integer, ForeignKey(Book.__tablename__ + '.id'))
    book = relationship('Book', foreign_keys=[book00_id])

    author00_id = Column(Integer, ForeignKey(Author.__tablename__ + '.id'))
    author = relationship('Author', foreign_keys=[author00_id])

    createdate = Column(DateTime, default=func.now())
    lastupdate = Column(DateTime, default=func.now(), onupdate=func.now())
    active = Column(Boolean, default=True)


class User(GenericBase, Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    login = Column(String(80), unique=True)
    email = Column(String(120))
    password = Column(String(100))

    # Flask-Login integration
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    # Required for administrative interface
    def __unicode__(self):
        return self.username


# # Delete hooks for models, delete files if models are getting deleted
# @listens_for(Book, 'after_delete')
# def del_file(mapper, connection, target):
#     if target.path:
#         try:
#             os.remove(op.join(file_path, target.path))
#         except OSError:
#             # Don't care if was not deleted because it does not exist
#             pass

#     if target.cover:
#         try:
#             os.remove(op.join(file_path, target.cover))
#         except OSError:
#             # Don't care if was not deleted because it does not exist
#             pass
