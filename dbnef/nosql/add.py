# encoding: utf-8
'''
@author: Minghao Guo
@contact: mh.guo0111@gmail.com
@software: srf_ct
@file: add.py
@date: 4/10/2019
@desc:
'''

import hashlib

from dbnef.config import sessionmaker, engine
from dbnef.utils import any_type_saver, file_hasher, file_deleter, resource_directory, load_schema, \
    append_schema
from .create_nosql_table import NosqlTable

schema_dict = load_schema()


def add(objs, *, kw: dict = {}):
    ''' tags are in kw, e.g. kw = {'tag': ['a', 'b']} '''
    schema_dict = load_schema()
    prefix = ('int', 'bool', 'float', 'str', 'List[float]', 'List[int]', 'List[bool]', 'List[str]')
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
            print(class_name)
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
                val = 'res:' + file_hasher(path_) + ext[1]
                new_path = resource_directory + val[4:]
                if os.path.isfile(new_path):
                    file_deleter(path_)
                else:
                    os.rename(path_, new_path)
                m.update(val.encode('utf-8'))
            elif spec.startswith(prefix):
                val = str(getattr(obj, key))
                m.update(val.encode('utf-8'))
            else:
                val = add(getattr(obj, key))[0]
                m.update(val.encode('utf-8'))

            kwargs.update({key: val})
        hash_ = 'sha256:' + m.hexdigest()

        ''' hash check '''
        ans = session.query(NosqlTable).filter(NosqlTable.hash == hash_).all()
        if not ans:
            class_name_obj = [NosqlTable(hash = hash_, key = 'classname', val = class_name)]
            val_objs = [NosqlTable(hash = hash_, key = key, val = val) for key, val in
                        kwargs.items()]
            kw_objs = []
            for k, v in kw.items():
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


def add_keywords(hash_, *, kw: dict = {}):
    kw_objs = []
    for k, v in kw.items():
        if isinstance(v, list):
            kw_objs += [NosqlTable(hash = hash_, key = k, val = v_) for v_ in v]
        else:
            kw_objs += [NosqlTable(hash = hash_, key = k, val = v)]
    Session = sessionmaker(bind = engine)
    session = Session()
    session.add_all(kw_objs)
    session.commit()
    return hash_
