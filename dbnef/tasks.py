# encoding: utf-8
'''
@author: Minghao Guo
@contact: mh.guo0111@gmail.com
@software: srf_ct
@file: tasks.py
@date: 3/29/2019
@desc:
'''

import hashlib
from getpass import getuser
import time
from .config import sessionmaker, engine
from .abstract import TaskTable
from .utils import convert_snake_to_Camel, tqdm, convert_Camal_to_snake
from .query import query_object_with_id
from .add_and_update_object import add_object_to_table

resource_directory = './tasks/'


def create_task(function = '', arguments = [], *, labels = [], depends = []):
    Session = sessionmaker(bind = engine)
    session = Session()

    kwargs = {'datetime': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time())))}
    kwargs.update({'creator': getuser()})
    kwargs.update({'labels': labels})
    kwargs.update({'status': 'READY'})
    m = hashlib.sha256()

    kwargs.update({'function': function})
    m.update(function.encode('utf-8'))
    kwargs.update({'arguments': arguments})
    for arg in arguments:
        m.update(arg.encode('utf-8'))

    depends_ = []
    for dep in depends:
        depends_.append(dep.__name__ + '==' + dep.__version__)
    depends_.sort()
    kwargs.update({'depends': depends_})
    m.update(str(depends_).encode('utf-8'))

    hash_ = m.hexdigest()
    kwargs.update({'hash_': hash_})
    table_obj = TaskTable(**kwargs)
    table_obj_ = session.query(TaskTable).filter(TaskTable.hash_ == hash_).all()
    if not table_obj_:
        session.add(table_obj)
        session.commit()
    else:
        print(f'Warning: the inserting task has already been inserted. locate at ' +
              f'Task/id={table_obj_[0].id}')
        table_obj = table_obj_[0]
    session.close()
    return table_obj, hash_


def run_task(ids = None, *, TYPE_BIND = None):
    if ids is None:
        return None
    if not isinstance(ids, list):
        ids = [ids]

    Session = sessionmaker(bind = engine)
    session = Session()
    tasks = session.query(TaskTable).filter(TaskTable.id.in_(ids)).all()
    outs = []
    for task in tqdm(tasks):
        func_table_class, func_id = task.function.split('-')
        func_id = int(func_id)
        function = query_object_with_id(func_table_class, ids = func_id, TYPE_BIND = TYPE_BIND)

        args = []
        for arg in task.arguments:
            arg_table_class, arg_id = arg.split('-')
            arg_id = int(func_id)
            args.append(query_object_with_id(arg_table_class, ids = arg_id, TYPE_BIND = TYPE_BIND))

        out = function(*args)
        outs.append(out)
        table_out = add_object_to_table(out, labels = task.labels)
        task.output = table_out[0].__tablename__ + '-' + str(table_out[0].id)
    session.commit()

    return outs
