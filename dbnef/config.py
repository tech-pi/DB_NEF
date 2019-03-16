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
from sqlalchemy import create_engine, MetaData
import contextlib
import numpy as np

engine = create_engine('postgresql://postgres:postgres@localhost/database', echo = False)


def create_session(engine = engine):
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind = engine)
    return Session()


Base = declarative_base()
Base.metadata.bind = engine

from sqlalchemy import Column, Integer, Float, String, Boolean, ForeignKey
from sqlalchemy.dialects import postgresql
import typing

table_support_type = {
    int: int,
    np.int64: int,
    np.int32: int,
    float: float,
    np.float32: float,
    np.float64: float,
    bool: bool,
    str: str,
    np.ndarray: list
}

colomn_support_type = {
    int: Column(Integer),
    float: Column(Float),
    bool: Column(Boolean),
    str: Column(String),
    typing.List[int]: Column(postgresql.ARRAY(Integer, dimensions = 1)),
    typing.List[float]: Column(postgresql.ARRAY(Float, dimensions = 1)),
    typing.List[bool]: Column(postgresql.ARRAY(Boolean, dimensions = 1)),
    typing.List[str]: Column(postgresql.ARRAY(String, dimensions = 1)),
    np.ndarray: Column(String)
}
