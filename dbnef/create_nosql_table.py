# encoding: utf-8
'''
@author: Minghao Guo
@contact: mh.guo0111@gmail.com
@software: srf_ct
@file: __init__.py
@date: 4/9/2019
@desc:
'''

from sqlalchemy import Column, Integer, String

from dbnef.config import create_base_class

with create_base_class() as Base:
    class NosqlTable(Base):
        __tablename__ = 'nosql_table'
        id = Column(Integer, primary_key = True)
        hash = Column(String)
        key = Column(String)
        val = Column(String, nullable = True)


def create_nosql_table():
    with create_base_class() as Base:
        class NosqlTable(Base):
            __tablename__ = 'nosql_table'
            id = Column(Integer, primary_key = True)
            hash = Column(String)
            key = Column(String)
            val = Column(String, nullable = True)

        Base.metadata.create_all()
