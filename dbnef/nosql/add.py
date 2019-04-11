# encoding: utf-8
'''
@author: Minghao Guo
@contact: mh.guo0111@gmail.com
@software: srf_ct
@file: add_objects.py
@date: 4/10/2019
@desc:
'''

import hashlib
import typing

import numpy as np

from dbnef.config import sessionmaker, engine
from dbnef.utils import any_type_saver, file_hasher, file_deleter, load_schema, \
    append_schema, get_ip, RESOURCE_PATH
from .create_nosql_table import NosqlTable

schema_dict = load_schema()
BASIC_TYPE_BIND_CONVERT = {int: 'int', float: 'float', bool: 'bool', str: 'str',
                           typing.List[int]: 'List[int]', typing.List[float]: 'List[float]',
                           typing.List[bool]: 'List[bool]', typing.List[str]: 'List[str]'}

BASIC_TYPE_BIND = {'int': int, 'float': float, 'bool': bool, 'str': str,
                   'List[int]': typing.List[int], 'List[float]': typing.List[float],
                   'List[bool]': typing.List[bool], 'List[str]': typing.List[str]}


def _to_string(o):
    if isinstance(o, np.ndarray):
        return np.array2string(o, separator = ',')
    else:
        return str(o)


def add_objects(objs, *, kw: dict = {}):
    ''' tags are in kw, e.g. kw = {'tag': ['a', 'b']} '''
    schema_dict = load_schema()
    Session = sessionmaker(bind = engine)
    session = Session()
    if not isinstance(objs, list):
        objs = [objs]

    out_hash = []

    for obj in objs:
        class_name = obj.__class__.__name__
        if class_name in schema_dict:
            schema = schema_dict[class_name]
        else:
            schema_dict = append_schema(obj.__class__, schema_dict)
            schema = schema_dict[class_name]

        m = hashlib.sha256()
        kwargs = {}
        for key, spec in schema.items():
            if getattr(obj, key) is None:
                val = None
            elif key == 'data':
                import os
                path_ = any_type_saver(getattr(obj, key))  # TODO should be take away
                ext = os.path.splitext(path_)
                val = get_ip() + ':' + RESOURCE_PATH + file_hasher(path_) + ext[1]
                new_path = val.split(':')[1]
                if os.path.isfile(new_path):
                    file_deleter(path_)
                else:
                    os.rename(path_, new_path)
                m.update(val.encode('utf-8'))
            elif spec[0] in BASIC_TYPE_BIND:
                val = _to_string(getattr(obj, key))
                m.update(val.encode('utf-8'))
            else:
                val = add_objects(getattr(obj, key))[0]
                m.update(val.encode('utf-8'))

            kwargs.update({key: val})
        hash_ = 'sha256:' + m.hexdigest()

        ''' hash check '''
        ans = session.query(NosqlTable.hash).filter(NosqlTable.hash == hash_).all()
        if not ans:
            class_name_obj = [NosqlTable(hash = hash_, key = 'classname', val = class_name)]
            val_objs = [NosqlTable(hash = hash_, key = key, val = val) for key, val in
                        kwargs.items()]
            kw_objs = []
            for k, v in kw.items():
                if k in schema:
                    print(f"Warning: keyword '{k}' is already in schema. ignored.")
                    continue
                if isinstance(v, list):
                    kw_objs += [NosqlTable(hash = hash_, key = k, val = v_) for v_ in v]
                else:
                    kw_objs += [NosqlTable(hash = hash_, key = k, val = v)]
            session.add_all(class_name_obj + val_objs + kw_objs)
            session.commit()
        else:
            pass
        out_hash.append(hash_)
    session.close()
    return out_hash


def add_dicts(dcts: dict, *, kw: dict = {}):
    ''' tags are in kw, e.g. kw = {'tag': ['a', 'b']} '''
    Session = sessionmaker(bind = engine)
    session = Session()

    out_hash = {}

    for key_, dct in dcts.items():
        assert 'classname' in dct
        m = hashlib.sha256()
        kwargs = {}
        for key, spec in dct.items():
            if getattr(dct, key) is None:
                val = None
            elif key == 'data':
                import os
                path_ = any_type_saver(getattr(dct, key))  # TODO should be take away
                ext = os.path.splitext(path_)
                val = get_ip() + ':' + RESOURCE_PATH + file_hasher(path_) + ext[1]
                new_path = val.split(':')[1]
                if os.path.isfile(new_path):
                    file_deleter(path_)
                else:
                    os.rename(path_, new_path)
                m.update(val.encode('utf-8'))
            elif spec[0] in BASIC_TYPE_BIND:
                val = _to_string(getattr(dct, key))
                m.update(val.encode('utf-8'))
            else:
                val = add_objects(getattr(dct, key))[0]
                m.update(val.encode('utf-8'))

            kwargs.update({key: val})
        hash_ = 'sha256:' + m.hexdigest()

        ''' hash check '''
        ans = session.query(NosqlTable.hash).filter(NosqlTable.hash == hash_).all()
        if not ans:
            class_name_obj = [NosqlTable(hash = hash_, key = 'classname', val = class_name)]
            val_objs = [NosqlTable(hash = hash_, key = key, val = val) for key, val in
                        kwargs.items()]
            kw_objs = []
            for k, v in kw.items():
                if k in dct:
                    print(f"Warning: keyword '{k}' is already in dct. ignored.")
                    continue
                if isinstance(v, list):
                    kw_objs += [NosqlTable(hash = hash_, key = k, val = v_) for v_ in v]
                else:
                    kw_objs += [NosqlTable(hash = hash_, key = k, val = v)]
            session.add_all(class_name_obj + val_objs + kw_objs)
            session.commit()
        else:
            pass
        out_hash.update({key_: hash_})
    session.close()
    return out_hash


def add(o, *, kw: dict = {}):
    if isinstance(o, dict):
        return add_dicts(o, kw = kw)
    else:
        return add_objects(o, kw = kw)


def add_keywords(hash_, *, kw: dict = {}, schema_check = True):
    Session = sessionmaker(bind = engine)
    session = Session()
    if schema_check:
        class_name = session.query(NosqlTable.val).filter(NosqlTable.key == 'classname',
                                                          NosqlTable.hash == hash_).all()[0][0]
        schema_keys = list(schema_dict[class_name].keys())
    else:
        schema_keys = []
    kw_objs = []
    for k, v in kw.items():
        if k in schema_keys:
            continue
        if k == 'classname':
            continue
        if isinstance(v, list):
            kw_objs += [NosqlTable(hash = hash_, key = k, val = v_) for v_ in v]
        else:
            kw_objs += [NosqlTable(hash = hash_, key = k, val = v)]
    session.add_all(kw_objs)
    session.commit()
    return hash_
