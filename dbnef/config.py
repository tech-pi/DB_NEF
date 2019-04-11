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

engine = create_engine('postgresql://postgres:postgres@localhost/pitech_db', echo = False)

Session = sessionmaker(bind = engine)
session = Session()

Base = declarative_base()
Base.metadata.bind = engine
