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
from scipy import sparse
from typing import List
from getpass import getuser
import time
from .utils import any_type_saver, file_hasher, file_deleter, is_dataclass, fields, \
    convert_Camal_to_snake
from .create_table_class import create_table
from .config import sessionmaker, engine

resource_directory = './resources/'


def add_object_to_table(obj, *, labels = []):
    Session = sessionmaker(bind = engine)
    session = Session()
    assert is_dataclass(obj)
    table_class = create_table(obj.__class__)

    kwargs = {'datetime': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time())))}
    kwargs.update({'creator': getuser()})
    kwargs.update({'labels': labels})
    kwargs.update({'status': 'READY'})
    m = hashlib.sha256()

    for spec in fields(obj.__class__):
        key = spec.name

        if getattr(obj, key) is None:
            val = None
        elif spec.type is int:
            val = int(getattr(obj, key))
            m.update(str(val).encode('utf-8'))
        elif spec.type is float:
            val = float(getattr(obj, key))
            m.update(str(val).encode('utf-8'))
        elif spec.type is bool:
            val = bool(getattr(obj, key))
            m.update(str(val).encode('utf-8'))
        elif spec.type is str:
            val = str(getattr(obj, key))
            m.update(str(val).encode('utf-8'))
        elif spec.type in (List[int], List[float], List[str], List[bool], list):
            val = getattr(obj, key)
            if isinstance(val, np.ndarray):
                if val.dtype in (np.int32, np.int64):
                    val = val.astype(int).tolist()
                elif val.dtype in (np.float32, np.float64):
                    val = val.astype(float).tolist()
            else:
                val = list(val)
            m.update(str(val).encode('utf-8'))
        elif spec.type is np.ndarray or spec.type is sparse.coo.coo_matrix:
            from .abstract import ResourceTable
            path_ = any_type_saver(getattr(obj, key))
            hash_ = file_hasher(path_)
            val_ = session.query(ResourceTable).filter(ResourceTable.hash_ == hash_).all()
            if not val_:
                val = ResourceTable(**{'datetime': kwargs['datetime'],
                                       'creator': kwargs['creator'],
                                       'labels': kwargs['labels'],
                                       'status': kwargs['status'],
                                       'url': path_, 'hash_': hash_})
                session.add(val)
            else:
                file_deleter(path_)
                val = val_[0]
                path_ = val.url
                print(
                    f'Warning: the inserting resource has already been inserted. locate at {val.id}')
            m.update(path_.encode('utf-8'))
        elif is_dataclass(spec.type):
            val, hash__, _ = add_object_to_table(getattr(obj, key), labels = labels)
            m.update(hash__.encode('utf-8'))
        else:
            raise NotImplementedError(f'type {spec.type} is not implemented yet.')

        if isinstance(val, (np.int32, np.int64)):
            val = int(val)
        elif isinstance(val, (np.float32, np.float64)):
            val = float(val)
        kwargs.update({key: val})
    hash_ = m.hexdigest()
    kwargs.update({'hash_': hash_})
    table_obj = table_class(**kwargs)
    table_obj_ = session.query(table_class).filter(table_class.hash_ == hash_).all()
    if not table_obj_:
        session.add(table_obj)
        session.commit()
        id_ = session.query(table_class.id).all()[-1][0]
    else:
        print(f'Warning: the inserting object has already been inserted. locate at ' +
              f'{convert_Camal_to_snake(obj.__class__.__name__)}/id={table_obj_[0].id}')
        table_obj = table_obj_[0]
        id_ = table_obj.id
    session.close()
    return table_obj, hash_, id_
