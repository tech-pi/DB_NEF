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
from .config import session


def update_status(table_name, *, ids, status):
    if status not in ('DELETED', 'READY', 'ARCHIVED', 'DEPRECATED'):
        raise ValueError('status must in (DELETED, READY, ARCHIVED, DEPRECATED)')
    if ids is None:
        return []
    if not isinstance(ids, list):
        ids = [ids]

    table_cls_name = convert_snake_to_Camel(table_name) + 'Table'
    if table_cls_name in TABLE_TYPE_BIND.keys():
        table_cls = TABLE_TYPE_BIND[table_cls_name]
    else:
        raise ValueError('create_table_class(TYPE_BIND[convert_snake_to_Camel(table_name)]')
    if not ids:
        outs = session.query(table_cls).all()
    else:
        outs = session.query(table_cls).filter(table_cls.id.in_(ids)).all()
    for out in outs:
        out.status = status
    session.commit()


def mark_archived(table_name, *, ids):
    update_status(table_name, ids = ids, status = 'ARCHIVED')


def mark_ready(table_name, *, ids):
    update_status(table_name, ids = ids, status = 'READY')


def mark_deprecated(table_name, *, ids):
    update_status(table_name, ids = ids, status = 'DEPRECATED')


def mark_deleted(table_name, *, ids):
    update_status(table_name, ids = ids, status = 'DELETED')
