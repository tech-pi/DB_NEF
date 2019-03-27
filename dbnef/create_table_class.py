# encoding: utf-8
'''
@author: Minghao Guo
@contact: mh.guo0111@gmail.com
@software: srf_ct
@file: add_and_update_object.py
@date: 3/12/2019
@desc:
'''

from typing import List

from sqlalchemy import Column, Integer, Float, String, Boolean, ForeignKey
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import relationship
import numpy as np

from dataclasses import is_dataclass, fields
from .utils import convert_Camal_to_snake, TYPE_BIND
from .config import Base, engine


def create_table_class(cls: type):
    table_class_name = cls.__name__ + 'Table'
    if 'TYPE_BIND' in globals() and table_class_name in TYPE_BIND.keys():
        table_class = TYPE_BIND[table_class_name]
    else:
        table_name = convert_Camal_to_snake(cls.__name__)
        kwargs = {'__tablename__': table_name, 'id': Column(Integer, primary_key = True)}

        for spec in fields(cls):
            name = spec.name
            if spec.type is int:
                kwargs.update({name: Column(Integer)})
            elif spec.type is float:
                kwargs.update({name: Column(Float)})
            elif spec.type is bool:
                kwargs.update({name: Column(Boolean)})
            elif spec.type is str:
                kwargs.update({name: Column(String)})
            elif spec.type is List[int]:
                kwargs.update({name: Column(postgresql.ARRAY(Integer, dimensions = 1))})
            elif spec.type is List[float]:
                kwargs.update({name: Column(postgresql.ARRAY(Float, dimensions = 1))})
            elif spec.type is List[bool]:
                kwargs.update({name: Column(postgresql.ARRAY(Boolean, dimensions = 1))})
            elif spec.type is List[str]:
                kwargs.update({name: Column(postgresql.ARRAY(String, dimensions = 1))})
            elif spec.type is np.ndarray:
                kwargs.update({name: Column(String)})
            elif is_dataclass(spec.type):
                kwargs.update({name + '_id': Column(Integer, ForeignKey(name + '.id'))})
                kwargs.update({name: relationship(spec.type.__name__ + 'Table')})
            else:
                raise NotImplementedError(f'type {spec.type} is not implemented yet.')

        kwargs.update({'__hash__': Column(String)})
        table_class = type(table_class_name, (Base,), kwargs)
        print(kwargs)
    TYPE_BIND.update({table_class_name: table_class})
    return table_class


def create_table(cls: type, *, commit = False):
    create_table_class(cls)
    if commit:
        Base.metadata.bind = engine
        Base.metadata.create_all()
