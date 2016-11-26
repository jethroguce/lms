import datetime

from decimal import Decimal

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Float, Integer, String, Boolean, DateTime, CHAR, TEXT
from sqlalchemy import Column, Sequence, Index, ForeignKey, func


class GenericBase(object):
    id = Column(Integer)
    createdate = Column(DateTime, default=func.now())

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


class T_Book(GenericBase):
    __tablename__ = 'book00'
    GenericBase.id = Column(Integer, Sequence(__tablename__ + '_id_seq'), primary_key=True)
    book_title = Column(String(100), nullable=False)
    book_code = Column(String(50), nullable=False)
    book_description = Column(TEXT)

    createdate = Column(DateTime, default=func.now())
    lastupdate = Column(DateTime, default=func.now(), onupdate=func.now())
    active = Column(Boolean, default=True)
