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
from .query import search


def delete_with_hash(hsh: str = None, fields: list = []):
    Session = sessionmaker(bind = engine)
    session = Session()
    if not fields:
        outs = session.query(NosqlTable).filter(NosqlTable.hash == hsh).all()
        for out in outs:
            session.delete(out)
    else:
        for f in fields:
            outs = session.query(NosqlTable).filter(NosqlTable.hash == hsh,
                                                    NosqlTable.key == f).all()
            for out in outs:
                session.delete(out)
    session.commit()
    session.close()
    return hsh


def delete(filters: dict = None, fields: list = []):
    if filters is None:
        return 0
    hashes = search(filters)
    for hsh in hashes:
        delete_with_hash(hsh, fields = fields)
    return 1
