# encoding: utf-8
'''
@author: Minghao Guo
@contact: mh.guo0111@gmail.com
@software: srf_ct
@file: query.py
@date: 3/13/2019
@desc:
'''
from sqlalchemy.orm import sessionmaker

from dbnef.config import engine
from dbnef.utils import load_schema
from .create_nosql_table import NosqlTable
from .query import search

schema_dict = load_schema()


def delete_with_hash(hsh: str = None, fields: list = [], schema_check = True):
    Session = sessionmaker(bind = engine)
    session = Session()
    if not fields:
        outs = session.query(NosqlTable).filter(NosqlTable.hash == hsh).all()
        for out in outs:
            session.delete(out)
    else:
        if schema_check:

            class_name = session.query(NosqlTable.val).filter(NosqlTable.key == 'classname',
                                                              NosqlTable.hash == hsh).all()[0][0]
            schema_keys = list(schema_dict[class_name].keys())
        else:
            schema_keys = []
        for f in fields:
            if f == 'classname':
                print('Warning: trying to delete field classname, Forbidden and Ignored.')
                continue
            if f in schema_keys:
                print(f'Warning: trying to delete field {f} which is in Schema, Forbidden and ' +
                      f'Ignored.')
                continue
            outs = session.query(NosqlTable).filter(NosqlTable.hash == hsh,
                                                    NosqlTable.key == f).all()
            for out in outs:
                session.delete(out)
    session.commit()
    session.close()
    return hsh


def delete(filters: dict = None, fields: list = [], schema_check = True):
    if filters is None:
        return 0
    hashes = search(filters)
    for hsh in hashes:
        delete_with_hash(hsh, fields = fields, schema_check = schema_check)
    return 1
