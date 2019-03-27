# encoding: utf-8
'''
@author: Minghao Guo
@contact: mh.guo0111@gmail.com
@software: srf_ct
@file: add_and_update_object.py
@date: 3/12/2019
@desc:
'''

import hashlib
import numpy as np
from typing import List
from .typing import is_dataclass
from .utils import any_type_saver, file_hasher
from .create_table_class import create_table_class


def parse_dataclass_to_table_object(obj):
    assert is_dataclass(obj)
    table_class = create_table_class(obj.__class__)

    kwargs = {}
    m = hashlib.sha256()

    for key, spec in obj.__class__.fields().items():
        if spec.type is int:
            val = int(getattr(obj, key))
        elif spec.type is float:
            val = float(getattr(obj, key))
        elif spec.type is bool:
            val = bool(getattr(obj, key))
        elif spec.type is str:
            val = str(getattr(obj, key))
        elif spec.type in (List[int], List[float], List[str], List[bool]):
            val = list(getattr(obj, key))
        elif spec.type is np.ndarray:
            val_ = any_type_saver(getattr(obj, key))
            val = file_hasher(val_)
        elif is_dataclass(spec.type):
            val = parse_dataclass_to_table_object(getattr(obj, key))
        else:
            raise NotImplementedError(f'type {spec.type} is not implemented yet.')

        if is_dataclass(val):
            m.update(hash(val))
        else:
            m.update(str(val).encode('utf-8'))
        kwargs.update({key: val})
    kwargs.update({'__hash__': m.hexdigest()})

    table_obj = table_class(**kwargs)
    return table_obj


def add_object_to_table(objs, commit = False):
    if not isinstance(objs, list):
        objs = [objs]
    table_objs = [parse_dataclass_to_table_object(obj) for obj in objs]

    if commit:
        from .config import create_session
        session = create_session()
        session.add(table_objs[0])
        session.commit()

    return table_objs
