# encoding: utf-8
"""
@author: Minghao Guo
@contact: mh.guo0111@gmail.com
@software: srf_ct
@file: config.py
@date: 3/13/2019
@desc:
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

ws1_engine_url = 'postgresql://postgres:postgres@192.168.1.111/nef_db'
ws2_engine_url = 'postgresql://postgres:postgres@localhost/pitech_nosql'
engine = create_engine(ws2_engine_url, echo = False)

Session = sessionmaker(bind = engine)
session = Session()

Base = declarative_base()
Base.metadata.bind = engine


def update_engine(engine_url):
    global engine, session, Base
    engine = create_engine(engine_url, echo = False)

    Session = sessionmaker(bind = engine)
    session = Session()

    Base = declarative_base()
    Base.metadata.bind = engine


1
