# encoding: utf-8
'''
@author: Minghao Guo
@contact: mh.guo0111@gmail.com
@software: srf_ct
@file: query.py
@date: 3/13/2019
@desc:
'''
import pandas as pd
from sqlalchemy.orm import sessionmaker

from dbnef.config import engine
from .create_nosql_table import NosqlTable


def query_fields_with_hash(hashes: list = None, *, fields = None):
    if hashes is None:
        return {}
    if not isinstance(hashes, list):
        hashes = [hashes]

    Session = sessionmaker(bind = engine)
    session = Session()
    out = {}
    for ind, hsh in enumerate(hashes):
        dct = {}
        for key, val in session.query(NosqlTable.key, NosqlTable.val).filter(NosqlTable.hash == \
                                                                             hsh).all():
            if val is None:
                val = None
            elif val.startswith('sha256'):
                val = query_fields_with_hash(val, fields = fields)['0']

            if fields is None or key in fields:
                if key in dct:
                    if not isinstance(dct[key], list):
                        dct[key] = [dct[key], val]
                    else:
                        dct[key].append(val)
                else:
                    dct[key] = val

        out.update({str(ind): dct})
    return out


def query_with_hash(hashes: list = None):
    return query_fields_with_hash(hashes)


def search(filters: dict = None):
    if filters is None:
        return {}
    Session = sessionmaker(bind = engine)
    session = Session()
    cond = []
    for key, val in filters.items():
        if not isinstance(val, list):
            val = [val]
        if None not in val:
            cond.extend(
                [getattr(NosqlTable, 'key') == key, getattr(NosqlTable, 'val').in_(val)])
        else:
            from sqlalchemy import or_
            cond.extend(
                [getattr(NosqlTable, 'key') == key, or_(getattr(NosqlTable, 'val').in_(val),
                                                        getattr(NosqlTable, 'val').is_(None))])

    return list({out[0] for out in session.query(NosqlTable.hash).filter(*cond).all()})


def query_fields(filters: dict = None, *, fields = None):
    if filters is None:
        return {}
    return query_fields_with_hash(search(filters), fields = fields)


def query(filters: dict = None):
    if filters is None:
        return {}
    return query_with_hash(search(filters))


def write_to_pandas(filters: dict):
    dct = query(filters)
    data = [dct_ for dct_ in dct.values()]
    return pd.DataFrame(data)
