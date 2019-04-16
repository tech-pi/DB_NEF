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

import numpy as np

from .config import create_session
from .create_nosql_table import NosqlTable
from .utils import load_schema_file, append_schema_file, local_data_saver, BASIC_TYPE_DICT


def _to_string(o):
    if isinstance(o, np.ndarray):
        return np.array2string(o, separator = ',')
    else:
        return str(o)


def add_objects(objs, *, kw: dict = {}):
    ''' tags are in kw, e.g. kw = {'tag': ['a', 'b']} '''

    if not isinstance(objs, list):
        objs = [objs]

    out_hash = []
    for obj in objs:

        schema_dict = load_schema_file()
        class_name = obj.__class__.__name__

        if class_name in schema_dict:
            schema = schema_dict[class_name]
        else:
            schema_dict = append_schema_file(obj.__class__)
            schema = schema_dict[class_name]

        m = hashlib.sha256()
        kwargs = {}
        for key, spec in schema.items():
            if getattr(obj, key) is None:
                val = None
            elif key == 'data':
                val = local_data_saver(getattr(obj, key))  # TODO should be take away
                m.update(val.encode('utf-8'))
            elif spec in BASIC_TYPE_DICT:
                val = _to_string(getattr(obj, key))
                m.update(val.encode('utf-8'))
            else:
                val = add_objects(getattr(obj, key))[0]
                m.update(val.encode('utf-8'))

            kwargs.update({key: val})
        hash_ = 'sha256:' + m.hexdigest()

        ''' hash check and commit'''
        with create_session() as session:
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
    return out_hash


def add_dicts(dcts: dict, *, kw: dict = {}):
    ''' tags are in kw, e.g. kw = {'tag': ['a', 'b']} '''

    out_hash = {}

    for key_, dct in dcts.items():
        assert 'classname' in dct
        m = hashlib.sha256()
        kwargs = dct
        for key, val in kwargs.items():
            val = _to_string(val)
            m.update(val.encode('utf-8'))
        hash_ = 'sha256:' + m.hexdigest()

        ''' hash check '''
        with create_session() as session:
            ans = session.query(NosqlTable.hash).filter(NosqlTable.hash == hash_).all()
            print(ans)
            if not ans:
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
                session.add_all(val_objs + kw_objs)
                session.commit()
                print(1)
            else:
                pass
        out_hash.update({key_: hash_})

    return out_hash


def add(o, *, kw: dict = {}):
    if isinstance(o, dict):
        print('adding dict')
        return add_dicts(o, kw = kw)
    else:
        print('adding obj')
        return add_objects(o, kw = kw)


def add_keywords(hash_, *, kw: dict = {}, schema_check = True):
    with create_session() as session:
        if schema_check:
            class_name = session.query(NosqlTable.val).filter(NosqlTable.key == 'classname',
                                                              NosqlTable.hash == hash_).all()[0][0]
            schema_keys = list(load_schema_file()[class_name].keys())
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
