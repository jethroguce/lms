import datetime

from decimal import Decimal

from sqlalchemy.orm import relationship
from sqlalchemy import Integer, String, Boolean, DateTime, TEXT, LargeBinary
from sqlalchemy import Column, Sequence, Index, ForeignKey, func

from lms import Base


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
    __tablename__ = 'department00'
    GenericBase.id = Column(Integer, Sequence(__tablename__ + '_id_seq'), primary_key=True)
    name = Column(String(100), nullable=False)
    books = relationship('Book')

    createdate = Column(DateTime, default=func.now())
    lastupdate = Column(DateTime, default=func.now(), onupdate=func.now())
    active = Column(Boolean, default=True)

    def __repr__(self):
        return self.name


class Book(GenericBase, Base):
    __tablename__ = 'book00'
    GenericBase.id = Column(Integer, Sequence(__tablename__ + '_id_seq'), primary_key=True)
    title = Column(String(300), nullable=False)
    code = Column(String(50), nullable=False)
    description = Column(TEXT)

    department00_id = Column(Integer, ForeignKey(Department.__tablename__ + '.id'))
    department = relationship('Department', foreign_keys=[department00_id])
    year = Column(Integer)

    authors = relationship('BookAuthor')
    content = relationship('BookContent')

    createdate = Column(DateTime, default=func.now())
    lastupdate = Column(DateTime, default=func.now(), onupdate=func.now())
    active = Column(Boolean, default=True)

    def __repr__(self):
        return self.title


class BookContent(GenericBase, Base):
    __tablename__ = 'book01'
    GenericBase.id = Column(Integer, Sequence(__tablename__ + '_id_seq'), primary_key=True)

    book00_id = Column(Integer, ForeignKey(Book.__tablename__ + '.id'))
    book = relationship('Book', foreign_keys=[book00_id])

    content = Column(LargeBinary)

    createdate = Column(DateTime, default=func.now())
    lastupdate = Column(DateTime, default=func.now(), onupdate=func.now())
    active = Column(Boolean, default=True)

    def __repr__(self):
        return self.content


class Author(GenericBase, Base):
    __tablename__ = 'author00'
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

