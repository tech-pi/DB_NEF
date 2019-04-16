# encoding: utf-8
'''
@author: Minghao Guo
@contact: mh.guo0111@gmail.com
@software: srf_ct
@file: utils.py
@date: 3/15/2019
@desc:
'''
import hashlib
import os
import platform
import re
import sys
import time
from dataclasses import fields as fields_official
from dataclasses import is_dataclass as is_dataclass_official
from getpass import getuser

import tqdm as tqdm_

TABLE_TYPE_BIND = {}

if 'Windows' in platform.system():
    separator = '\\'
else:
    separator = '/'

DATABASE_PATH = os.environ['HOME'] + separator + 'Database_nef' + separator
RESOURCE_PATH = DATABASE_PATH + 'resources' + separator
SCHEMA_PATH = DATABASE_PATH + 'schemas' + separator


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


NECESSARIES = ('_sa_instance_state', 'id', 'state', 'add', 'submit', 'finish', 'depends',
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


def get_username():
    return getuser()
