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
from getpass import getuser
import time
from .utils import any_type_saver, file_hasher, is_dataclass
from .create_table_class import create_table_class, create_table
from .config import session

resource_directory = './resources/'


def add_object_to_table(obj, *, labels = []):
    assert is_dataclass(obj)
    table_class = create_table(obj.__class__, commit = True)

    kwargs = {'datetime': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time())))}
    kwargs.update({'creator': getuser()})
    kwargs.update({'labels': labels})
    kwargs.update({'status': 'READY'})
    m = hashlib.sha256()

    for key, spec in obj.__class__.fields().items():
        if getattr(obj, key) is None:
            val = None
        elif spec.type is int:
            val = int(getattr(obj, key))
        elif spec.type is float:
            val = float(getattr(obj, key))
        elif spec.type is bool:
            val = bool(getattr(obj, key))
        elif spec.type is str:
            val = str(getattr(obj, key))
        elif spec.type in (List[int], List[float], List[str], List[bool], list):
            val = list(getattr(obj, key))
        elif spec.type is np.ndarray:
            val_ = any_type_saver(getattr(obj, key))
            val = file_hasher(val_)
        elif is_dataclass(spec.type):
            val, __hash__ = add_object_to_table(getattr(obj, key), labels = labels)
        else:
            raise NotImplementedError(f'type {spec.type} is not implemented yet.')

        if is_dataclass(val):
            m.update(hash(val))
        else:
            m.update(str(val).encode('utf-8'))
        kwargs.update({key: val})
    kwargs.update({'__hash__': m.hexdigest()})

    table_obj = table_class(**kwargs)
    session.add(table_obj)
    session.commit()
    return table_obj, m.hexdigest()
