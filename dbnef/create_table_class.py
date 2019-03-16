# encoding: utf-8
'''
@author: Minghao Guo
@contact: mh.guo0111@gmail.com
@software: srf_ct
@file: add_and_update_object.py
@date: 3/12/2019
@desc:
'''

from typing import Dict, Union, List

from sqlalchemy import Column, Integer, Float, String, Boolean, ForeignKey
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import relationship
from sqlalchemy.util import symbol

from .typing import TYPE_BIND, DataClass
from .utils import convert_Camal_to_snake
from .config import Base, table_support_type, colomn_support_type


def create_table_class(cls: type):
    if not issubclass(cls, DataClass):
        raise TypeError(f'type {cls} is not a DataClass typed class')
    table_name = convert_Camal_to_snake(cls.__name__)
    table_class_name = cls.__name__ + 'Table'
    if 'TYPE_BIND' in globals() and table_class_name in TYPE_BIND.keys():
        table_class = TYPE_BIND[table_class_name]
    else:
        kwargs: Dict[str, Union[str, Column, symbol, bool]]
        kwargs.update({'__tablename__': table_name})
        kwargs.update({'id': Column(Integer, primary_key = True)})

        for key, val in cls.fields().items():
            if issubclass(val.type, DataClass):
                kwargs.update({key + '_id': Column(Integer, ForeignKey(key + '.id'))})
                kwargs.update({key: relationship(val.type.__name__ + 'Table')})
            elif val.type in colomn_support_type:
                kwargs.update({key: colomn_support_type[val.type]})
            else:
                raise NotImplementedError(f'type {val.type} is not implemented yet.')

        kwargs.update({'hash_': colomn_support_type[str]})
        kwargs.update({'extend_existing': colomn_support_type[bool]})
        table_class = type(table_class_name, (Base,), kwargs)

    TYPE_BIND.update({table_class_name: table_class})
    return table_class


def create_table(cls: type, *, commit = False):
    create_table_class(cls)
    if commit:
        Base.metadata.create_all()
