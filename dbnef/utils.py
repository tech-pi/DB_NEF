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
import tqdm
from getpass import getuser
from .typing import is_dataclass


def is_notebook():
    '''check if the current environment is `ipython`/ `notebook`
    '''
    return 'ipykernel' in sys.modules


is_ipython = is_notebook


def _tqdm(*args, **kwargs):
    '''same as tqdm.tqdm
    Automatically switch between `tqdm.tqdm` and `tqdm.tqdm_notebook` accoding to the runtime
    environment.
    '''
    if is_notebook():
        return tqdm.tqdm_notebook(*args, **kwargs)
    else:
        return tqdm.tqdm(*args, **kwargs)


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


KW_EXCEPTION = ('_sa_instance_state', 'id', 'state', 'create', 'submit', 'finish', 'depends',
                'scheduler', 'backend', 'workdir', 'id_on_backend', 'state_on_backend', 'worker',
                'script', 'inputs', 'outputs', 'fn', 'name', 'creator', 'labels', 'datetime',
                '_hash', 'tasks', 'data_shape', 'extend_existing')


def dict_hasher(dct: dict, exception = KW_EXCEPTION):
    m = hashlib.sha256()
    for key, val in dct.items():
        if key in exception:
            continue
        m.update(str(val).encode('utf-8'))
    return m.hexdigest()


def dataclass_hasher(obj, exception = KW_EXCEPTION):
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
    if isinstance(data, np.ndarray):
        _path = get_hash_of_timestamp()
        path = resource_directory + _path + '.npy'
        np.save(path, data)
        return path
    else:
        raise NotImplementedError(f'`any_saver` does not support type {type(data)} saving. ')


def parse_table_class(table_name: str):
    from .create_table_class import create_table

    class_name = convert_snake_to_Camel(table_name)
    table_class_name = class_name + 'Table'
    if table_class_name in globals():
        table_class = globals()[table_class_name]
    elif class_name in globals():
        table_class = create_table(globals()[class_name], commit = False)
    elif 'TYPE_BIND' in globals():
        TYPE_BIND = globals()['TYPE_BIND']
        if table_class_name in TYPE_BIND:
            table_class = TYPE_BIND[table_class_name]
        elif class_name in TYPE_BIND:
            table_class = create_table(globals()['TYPE_BIND'][class_name], commit = False)
    else:
        raise ValueError(f'cannot find any envidence of {class_name} to do deserialization')
    return table_class
