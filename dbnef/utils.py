# encoding: utf-8
'''
@author: Minghao Guo
@contact: mh.guo0111@gmail.com
@software: srf_ct
@file: utils.py
@date: 3/15/2019
@desc:
'''
import os
import platform
import re
import sys
import time
import hashlib
import tqdm as tqdm_
from getpass import getuser
from dataclasses import is_dataclass as is_dataclass_official
from dataclasses import fields as fields_official

TABLE_TYPE_BIND = {}


def is_dataclass(cls):
    if is_dataclass_official(cls):
        return True
    try:
        cls.fields()
        return True
    except:
        return False


def fields(cls):
    if is_dataclass_official(cls):
        return fields_official(cls)
    else:
        try:
            return list(cls.fields().values())
        except:
            raise ValueError


def is_notebook():
    '''check if the current environment is `ipython`/ `notebook`
    '''
    return 'ipykernel' in sys.modules


is_ipython = is_notebook


def tqdm(*args, **kwargs):
    '''same as tqdm.tqdm
    Automatically switch between `tqdm.tqdm` and `tqdm.tqdm_notebook` accoding to the runtime
    environment.
    '''
    if is_notebook():
        return tqdm_.tqdm_notebook(*args, **kwargs)
    else:
        return tqdm_.tqdm(*args, **kwargs)


if 'Windows' in platform.system():
    separator = '\\'
else:
    separator = '/'

resource_directory = os.path.abspath(os.path.dirname(os.path.abspath(__file__))) + separator + \
                     'resources' + separator


def convert_Camal_to_snake(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def convert_snake_to_Camel(name):
    out = ''
    for ele in name.split('_'):
        out += ele.capitalize()
    return out


def get_timestamp():
    return time.time()


def get_current_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(get_timestamp())))


def get_hash_of_timestamp():
    m = hashlib.sha256()
    timestamp = time.time()
    m.update(str(timestamp).encode('utf-8'))
    return m.hexdigest()


NECESSARIES = ('_sa_instance_state', 'id', 'state', 'create', 'submit', 'finish', 'depends',
               'scheduler', 'backend', 'workdir', 'id_on_backend', 'state_on_backend', 'worker',
               'script', 'inputs', 'outputs', 'fn', 'creator', 'labels', 'datetime',
               'hash_', 'tasks', 'data_shape', 'extend_existing', 'status')

EXCEPTIONS = NECESSARIES + ()


def dict_hasher(dct: dict, exception = NECESSARIES):
    m = hashlib.sha256()
    for key, val in dct.items():
        if key in exception:
            continue
        m.update(str(val).encode('utf-8'))
    return m.hexdigest()


def dataclass_hasher(obj, exception = NECESSARIES):
    m = hashlib.sha256()
    dct = obj.as_dict(recurse = False)
    for key, val in dct.items():
        if key in exception:
            continue
        elif is_dataclass(val):
            m.update(str(val.as_dict(recurse = False)).encode('utf-8'))
        else:
            m.update(str(val).encode('utf-8'))
    return m.hexdigest()


def file_hasher(path: str):
    if os.path.isdir(path):
        raise ValueError('Only file can be hashed')

    BLOCKSIZE = 65536
    m = hashlib.sha256()

    with open(path, 'rb') as fin:
        buf = fin.read(BLOCKSIZE)
        while len(buf) > 0:
            m.update(buf)
            buf = fin.read(BLOCKSIZE)
    return m.hexdigest()


def get_username():
    return getuser()


def any_type_saver(data):
    import numpy as np
    from scipy import sparse
    if isinstance(data, np.ndarray):
        _path = get_hash_of_timestamp()
        path = resource_directory + _path + '.npy'
        np.save(path, data)
        return path
    elif isinstance(data, sparse.coo.coo_matrix):
        _path = get_hash_of_timestamp()
        path = resource_directory + _path + '.npz'
        sparse.save_npz(path, data)
        return path
    else:
        raise NotImplementedError(f'`any_saver` does not support type {type(data)} saving. ')


def file_deleter(path_):
    try:
        os.remove(path_)
    except:
        ValueError(f'removing file at {path_} failed')


def any_type_loader(path_: str):
    import numpy as np
    from scipy import sparse
    if path_.endswith('npy'):
        return np.load(path_)
    elif path_.endswith('npz'):
        return sparse.load_npz(path_)
    else:
        raise NotImplementedError(f'`any_type_loader` does not {path_} loading. ')


def parse_table_class(table_name: str):
    from .create_table_class import create_table

    class_name = convert_snake_to_Camel(table_name)
    table_class_name = class_name + 'Table'
    if table_class_name in globals():
        table_class = globals()[table_class_name]
    elif class_name in globals():
        table_class = create_table(globals()[class_name], commit = False)
    elif 'TABLE_TYPE_BIND' in globals():
        TYPE_BIND = globals()['TABLE_TYPE_BIND']
        if table_class_name in TYPE_BIND:
            table_class = TYPE_BIND[table_class_name]
        elif class_name in TYPE_BIND:
            table_class = create_table(globals()['TABLE_TYPE_BIND'][class_name], commit = False)
    else:
        raise ValueError(f'cannot find any envidence of {class_name} to do deserialization')
    return table_class


TYPE_BIND = {}
