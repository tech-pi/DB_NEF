# encoding: utf-8
'''
@author: Minghao Guo
@contact: mh.guo0111@gmail.com
@software: srf_ct
@file: query.py
@date: 3/13/2019
@desc:
'''

from .config import session
from .utils import convert_snake_to_Camel
from .create_table_class import create_table_class
from sqlalchemy.inspection import _self_inspects
from .config import create_session


@_self_inspects
class Query(object):
    pass


def select(table_name: str, fields = [], conditions = [], order_by = []):
    session = create_session()
    table_class_name = convert_snake_to_Camel(table_name) + 'Table'
    if table_class_name in globals():
        table_class = globals()[table_class_name]
    elif 'TYPE_BIND' in globals() and table_class_name in globals()['TYPE_BIND']:
        table_class = globals()['TYPE_BIND'][table_class_name]
    else:
        raise ValueError(f'can not find any evidences in globals() of {table_name}')

    query = session.query(table_class)
    for cond in list(conditions):
        if query._criterion is None:
            query._criterion = [table_class_name + '.' + cond]
        else:
            query._criterion = query._criterion + [table_class_name + '.' + cond]

    cond_dict = {}
    for key, val in conditions.items():
        if not isinstance(val, list):
            val = [val]
        cond_dict.update({key: val})
    outs = session.query(table_class).filter()
#
#
# def select_with_id(table_name, ids = None):
#     if ids is None:
#         return []
#     if not isinstance(ids, list):
#         ids = [ids]
#
#     cls = TYPE_BIND[convert_snake_to_Camel(table_name)]
#     table_cls_name = convert_snake_to_Camel(table_name) + 'Table'
#     if table_cls_name in TYPE_BIND.keys():
#         table_cls = TYPE_BIND[table_cls_name]
#     else:
#         create_schema(TYPE_BIND[convert_snake_to_Camel(table_name)])
#         table_cls = TYPE_BIND[table_cls_name]
#     outs = session.query(table_cls).filter(table_cls.id.in_(ids)).all()
#     objs = []
#     for out in outs:
#         kwargs = {}
#         for key, val in out.__dict__.items():
#             if key == 'data':
#                 import numpy as np
#                 kwargs.update({key: np.load(val)})
#
#             elif key.endswith('_id'):
#                 val_ = select_with_id(key[:-3], ids = val)
#                 kwargs.update({key[:-3]: val_})
#             elif key not in kw_exception:
#                 kwargs.update({key: val})
#             else:
#                 pass
#         objs.append(cls(**kwargs))
#
#     if len(ids) == 1:
#         return objs[0]
#     else:
#         return objs
#
#
# def run_task(table_names, ids, *, labels):
#     from .insert_object import insert_object
#     table_name1, table_name2 = table_names
#
#     for id_pair in _tqdm(ids):
#         func = select_with_id(table_name1, id_pair[0])
#         args = select_with_id(table_name2, id_pair[1])
#         insert_object(func(args, labels = labels), commit = True, labels = labels + ['final'])
#
#
# def get_all_hash(table_name):
#     table_cls_name = convert_snake_to_Camel(table_name) + 'Table'
#     if table_cls_name in TYPE_BIND.keys():
#         table_cls = TYPE_BIND[table_cls_name]
#     else:
#         create_schema(TYPE_BIND[convert_snake_to_Camel(table_name)])
#         table_cls = TYPE_BIND[table_cls_name]
#     outs = session.query(table_cls.hash_).all()
#     return outs
#
#
# def update_labels(table_name, ids, labels = [], mode = 'add'):
#     if ids is None:
#         return []
#     if not isinstance(ids, list):
#         ids = [ids]
#
#     table_cls_name = convert_snake_to_Camel(table_name) + 'Table'
#     if table_cls_name in TYPE_BIND.keys():
#         table_cls = TYPE_BIND[table_cls_name]
#     else:
#         create_schema(TYPE_BIND[convert_snake_to_Camel(table_name)])
#         table_cls = TYPE_BIND[table_cls_name]
#     outs = session.query(table_cls).filter(table_cls.id.in_(ids)).all()
#     for out in outs:
#         if mode == 'add':
#             out.labels = out.labels + labels
#         elif mode == 'new':
#             out.labels = labels
#         else:
#             raise ValueError
#     session.commit()
