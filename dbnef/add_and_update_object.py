# encoding: utf-8
'''
@author: Minghao Guo
@contact: mh.guo0111@gmail.com
@software: srf_ct
@file: add_and_update_object.py
@date: 3/12/2019
@desc:
'''

from typing import Dict, Any
import hashlib

from .typing import DataClass
from .utils import any_type_saver
from .config import table_support_type, create_session
from .create_table_class import create_table_class


def parse_dataclass_to_table_object(obj: DataClass):
    table_class = create_table_class(obj.__class__)

    kwargs: Dict[str, Any]
    m = hashlib.sha256()
    for key, spec in obj.fields().items():
        if key == 'data':
            path_ = any_type_saver(getattr(obj, key))
            kwargs.update({key: path_})
            m.update(path_.encode('utf-8'))
        elif issubclass(spec.type, DataClass):
            sub_, hash_ = parse_dataclass_to_table_object(getattr(obj, key))
            kwargs.update(({key: sub_}))
            m.update(hash_.encode('utf-8'))
        elif spec.type in table_support_type:
            val = getattr(obj, key)
            val_ = table_support_type[type(val)](val)
            kwargs.update({key: val_})
            m.update(str(val_).encode('utf-8'))
        else:
            raise NotImplementedError(f'type {val.type} is not implemented yet.')

    hash_ = m.hexdigest()
    kwargs.update({'hash_': hash_})
    kwargs.update({'extend_existing': True})
    table_obj = table_class(**kwargs)
    return table_obj, hash_


def add_object_to_table(objs, commit = False):
    if not isinstance(objs, list):
        objs = [objs]
    table_objs = [parse_dataclass_to_table_object(obj)[0] for obj in objs]
    session = create_session()

    if commit:
        session.add_all(table_objs)
        session.commit()
    try:
        session.rollback()
    except:
        pass
    return table_objs
