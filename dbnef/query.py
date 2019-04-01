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
from .utils import any_type_loader, EXCEPTIONS, convert_snake_to_Camel, convert_Camal_to_snake
from .create_table_class import create_table_class
from .abstract import ResourcesTable


def query_object_with_id(table_name, *, ids = None, TYPE_BIND = None):
    class_name = convert_snake_to_Camel(table_name)
    if TYPE_BIND is not None:
        cls = TYPE_BIND[class_name]
    elif class_name in globals():
        cls = globals()[class_name]
    else:
        raise ValueError(f'cannot find any declaration of {class_name}')

    if cls.__name__.endswith('Table'):
        raise ValueError('Use its corresponding class as argument')

    Session = sessionmaker(bind = engine)
    session = Session()
    if ids is None:
        ids = []
    if not isinstance(ids, list):
        ids = [ids]

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
            if key == 'res_id':
                path_ = session.query(ResourcesTable.url).filter(ResourcesTable.id == val).all()[0][0]
                kwargs.update({'data': any_type_loader(path_)})
            elif key.endswith('_id'):
                sub_table_name = key[:-3]
                if val is None:
                    val_ = None
                else:
                    val_ = query_object_with_id(sub_table_name, ids = val, TYPE_BIND = TYPE_BIND)
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


def query_last_id(table_name):
    Session = sessionmaker(bind = engine)
    session = Session()

    table_class_name = convert_snake_to_Camel(table_name) + 'Table'
    if table_class_name in TABLE_TYPE_BIND:
        table_cls = TABLE_TYPE_BIND[table_class_name]
    else:
        raise ValueError(f'cannot find table class {table_class_name} in TABLE_TYPE_BIND')
    out = session.query(table_cls.id).order_by(table_cls.id.desc()).first()
    return int(out[0])


def query_last_object(table_name, *, TYPE_BIND = None):
    class_name = convert_snake_to_Camel(table_name)
    if TYPE_BIND is not None:
        cls = TYPE_BIND[class_name]
    elif class_name in globals():
        cls = globals()[class_name]
    else:
        raise ValueError(f'cannot find any declaration of {class_name}')

    if cls.__name__.endswith('Table'):
        raise ValueError('Use its corresponding class as argument')

    Session = sessionmaker(bind = engine)
    session = Session()

    table_class_name = class_name + 'Table'
    if table_class_name in TABLE_TYPE_BIND:
        table_cls = TABLE_TYPE_BIND[table_class_name]
    else:
        create_table_class(cls)
        table_cls = TABLE_TYPE_BIND[table_class_name]
    out = session.query(table_cls).order_by(table_cls.id.desc()).first()

    kwargs = {}
    for key, val in out.__dict__.items():
        if key == 'res_id':
            path_ = session.query(ResourcesTable.url).filter(ResourcesTable.id == val).all()[0][0]
            kwargs.update({'data': any_type_loader(path_)})
        elif key.endswith('_id'):
            sub_table_name = key[:-3]
            if val is None:
                val_ = None
            else:
                val_ = query_object_with_id(sub_table_name, ids = val, TYPE_BIND = TYPE_BIND)
            kwargs.update({key[:-3]: val_})
        elif key not in EXCEPTIONS:
            kwargs.update({key: val})
        else:
            pass

    return cls(**kwargs)


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
