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
from sqlalchemy.orm import scoped_session, sessionmaker


engine = create_engine('postgresql://postgres:postgres@localhost/test_database3', echo = False)


Session = sessionmaker(bind = engine)
session = Session()

Base = declarative_base()
Base.metadata.bind = engine
