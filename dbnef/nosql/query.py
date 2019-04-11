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
            if val.startswith('sha256'):
                val = query_fields_with_hash(val, fields = fields)['0']
            if key in fields or fields is None:
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


#
# def query_with_hash(hashes: list = None):
#     if hashes is None:
#         return {}
#     if not isinstance(hashes, list):
#         hashes = [hashes]
#
#     Session = sessionmaker(bind = engine)
#     session = Session()
#     out = {}
#     for ind, hsh in enumerate(hashes):
#         dct = {}
#         for key, val in session.query(NosqlTable.key, NosqlTable.val).filter(NosqlTable.hash == \
#                                                                              hsh).all():
#             if val.startswith('sha256'):
#                 val = query_with_hash(val)['0']
#             if key in dct:
#                 if not isinstance(dct[key], list):
#                     dct[key] = [dct[key], val]
#                 else:
#                     dct[key].append(val)
#             else:
#                 dct[key] = val
#         out.update({str(ind): dct})
#     return out

def search(filters: dict = None):
    if filters is None:
        return {}
    Session = sessionmaker(bind = engine)
    session = Session()
    cond = True
    for key, val in filters.items():
        if isinstance(val, list):
            cond = cond and getattr(NosqlTable, 'key') == key and getattr(NosqlTable, 'val') in val
        else:
            cond = cond and getattr(NosqlTable, 'key') == key and getattr(NosqlTable, 'val') == val
    return list({out[0] for out in session.query(NosqlTable.hash).filter(cond).all()})


def query_fields(filters: dict = None, *, fields = None):
    if filters is None:
        return {}
    return query_fields_with_hash(search(filters), fields = fields)


def query(filters: dict = None):
    if filters is None:
        return {}
    return query_with_hash(search(filters))
