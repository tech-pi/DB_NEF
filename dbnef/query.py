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

from .config import engine
from .utils import TABLE_TYPE_BIND
from .utils import any_type_loader, EXCEPTIONS
from .create_table_class import create_table_class


def query_object_with_id(cls, *, ids = None):
    Session = sessionmaker(bind = engine)
    session = Session()
    if ids is None:
        ids = []
    if not isinstance(ids, list):
        ids = [ids]

    class_name = cls.__name__
    table_class_name = class_name + 'Table'
    if table_class_name in TABLE_TYPE_BIND:
        table_cls = TABLE_TYPE_BIND[table_class_name]
    else:
        create_table_class(cls)
        table_cls = TABLE_TYPE_BIND[table_class_name]
    if not ids:
        outs = session.query(table_cls).all()
    else:
        outs = session.query(table_cls).filter(table_cls.id.in_(ids)).all()

    objs = []
    for out in outs:
        kwargs = {}
        for key, val in out.__dict__.items():
            if key == 'data':
                kwargs.update({key: any_type_loader(val)})
            elif key.endswith('_id'):
                sub_class = cls.fields()[key[:-3]].type
                val_ = query_object_with_id(sub_class, ids = val)
                kwargs.update({key[:-3]: val_})
            elif key not in EXCEPTIONS:
                kwargs.update({key: val})
            else:
                pass

        objs.append(cls(**kwargs))

    if len(ids) == 1:
        return objs[0]
    else:
        return objs


def query_id_with_filter(table_class, *, filters = []):
    Session = sessionmaker(bind = engine)
    session = Session()

    if not filters:
        return session.query(table_class.id).all()

    query = session.query(table_class.id)

    for filt in list(filters):
        query = query.filter(filt)
    return [id_[0] for id_ in query.all()]


def _intersection(lst1, lst2):
    lst3 = [value for value in lst1 if value in lst2]
    return lst3


def query_id_with_filter_and_labels(table_class, *, filters = [], label_filters = []):
    ids = query_id_with_filter(table_class, filters = filters)
    if not label_filters:
        return ids
    Session = sessionmaker(bind = engine)
    session = Session()
    outs = session.query(table_class).filter(table_class.id.in_(ids)).all()

    ids_out = []
    for out in outs:
        if not _intersection(out.labels, label_filters):
            continue
        ids_out.append(out.id)
    return ids_out


def _query_all_hash(cls):
    Session = sessionmaker(bind = engine)
    session = Session()

    class_name = cls.__name__
    table_class_name = class_name + 'Table'
    if table_class_name in TABLE_TYPE_BIND:
        table_cls = TABLE_TYPE_BIND[table_class_name]
    else:
        create_table_class(cls)
        table_cls = TABLE_TYPE_BIND[table_class_name]
    return session.query(table_cls.id, table_cls.__hash__).all()
