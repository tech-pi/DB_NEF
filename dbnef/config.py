# encoding: utf-8
"""
@author: Minghao Guo
@contact: mh.guo0111@gmail.com
@software: srf_ct
@file: config.py
@date: 3/13/2019
@desc:
"""
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine


engine = create_engine('postgresql://postgres:postgres@localhost/test_database', echo = True)


def create_session():
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind = engine)
    return Session()


Base = declarative_base()
Base.metadata.bind = engine
