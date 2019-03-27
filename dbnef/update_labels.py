# encoding: utf-8
'''
@author: Minghao Guo
@contact: mh.guo0111@gmail.com
@software: srf_ct
@file: update_labels.py
@date: 3/25/2019
@desc:
'''
from .utils import convert_snake_to_Camel, TABLE_TYPE_BIND
from .create_table_class import create_table_class
from .config import session


def update_labels(table_name, *, ids, labels = [], mode = 'add'):
    if ids is None:
        return []
    if not isinstance(ids, list):
        ids = [ids]

    table_cls_name = convert_snake_to_Camel(table_name) + 'Table'
    if table_cls_name in TABLE_TYPE_BIND.keys():
        table_cls = TABLE_TYPE_BIND[table_cls_name]
    else:
        table_cls = create_table_class(TABLE_TYPE_BIND[convert_snake_to_Camel(table_name)])
    if not ids:
        outs = session.query(table_cls).all()
    else:
        outs = session.query(table_cls).filter(table_cls.id.in_(ids)).all()
    for out in outs:
        if mode == 'add':
            out.labels = out.labels + labels
        elif mode == 'new':
            out.labels = labels
        else:
            raise ValueError('only support mode in (new, add)')
    session.commit()


def clear_labels(table_name, *, ids):
    if ids is None:
        return []
    if not isinstance(ids, list):
        ids = [ids]

    table_cls_name = convert_snake_to_Camel(table_name) + 'Table'
    if table_cls_name in TABLE_TYPE_BIND.keys():
        table_cls = TABLE_TYPE_BIND[table_cls_name]
    else:
        table_cls = create_table_class(TABLE_TYPE_BIND[convert_snake_to_Camel(table_name)])
    if not ids:
        outs = session.query(table_cls).all()
    else:
        outs = session.query(table_cls).filter(table_cls.id.in_(ids)).all()
    for out in outs:
        out.labels = []
    session.commit()
