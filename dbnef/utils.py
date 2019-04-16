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
import json
import os
import platform
import typing

import numpy as np
from scipy import sparse

if 'Windows' in platform.system():
    separator = '\\'
else:
    separator = '/'

DATABASE_DIR = os.environ['HOME'] + separator + 'Database_nef' + separator
RESOURCE_DIR = DATABASE_DIR + 'resources' + separator
CACHE_DIR = DATABASE_DIR + 'caches' + separator
SCHEMA_PATH = os.path.abspath(os.path.dirname(os.path.abspath(__file__))) + 'schema.json'
_PATH_LIST = [DATABASE_DIR, RESOURCE_DIR, CACHE_DIR]

for _path in _PATH_LIST:
    if not os.path.isdir(_path):
        os.mkdir(_path)

BASIC_TYPE_DICT = {'int': int,
                   'str': str,
                   'bool': bool,
                   'float': float,
                   'List[int]': typing.List[int],
                   'List[str]': typing.List[str],
                   'List[bool]': typing.List[bool],
                   'List[float]': typing.List[float]}

BASIC_TYPE_DICT_REVERT = {int: 'int', float: 'float', bool: 'bool', str: 'str',
                          typing.List[int]: 'List[int]', typing.List[float]: 'List[float]',
                          typing.List[bool]: 'List[bool]', typing.List[str]: 'List[str]'}

if not os.path.isfile(SCHEMA_PATH):
    with open(SCHEMA_PATH, 'w') as fout:
        json.dump({}, fout, indent = 4, separators = (',', ':'))


def load_schema_file(path = SCHEMA_PATH):
    with open(path, 'r') as fin:
        dct = json.load(fin)
    return dct


def append_schema(schema, dct: dict = None):
    if dct is None:
        return schema
    if isinstance(dct, dict):
        schema.update(dct)
    elif isinstance(dct, type):
        cls_dct = {}
        for k, v in dct.__annotations__.items():
            if v in BASIC_TYPE_DICT_REVERT:
                cls_dct.update({k: BASIC_TYPE_DICT_REVERT[v]})
            elif v.__name__ in schema or v.__name__ in cls_dct:
                continue
            elif k == 'data':
                cls_dct.update({k: 'str'})
            else:
                append_schema(schema, v)
                cls_dct.update({k: v.__name__})
        cls_dct = {dct.__name__: cls_dct}
        schema.update(cls_dct)
    else:
        raise NotImplementedError

    return schema


def append_schema_file(dct: dict = None, path = SCHEMA_PATH):
    with open(path, 'r') as fin:
        schema = json.load(fin)
    if dct is None:
        return schema

    append_schema(schema, dct)
    with open(path, 'w') as fout:
        json.dump(schema, fout)
    return schema


def file_hasher(path: str):
    import os
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


def local_data_saver(data = None):
    import numpy as np
    from scipy import sparse
    from basenef.utils import get_hash_of_timestamp

    cache_path = CACHE_DIR + get_hash_of_timestamp()
    if data is None:
        return -1
    if isinstance(data, np.ndarray):
        np.save(cache_path + '.npy', data)
        ext = '.npy'
        cache_path += ext
    elif isinstance(data, sparse.coo_matrix):
        sparse.save_npz(cache_path + '.npz', data)
        ext = '.npz'
        cache_path += ext
    else:
        raise ValueError(f'Unsupported data type {data.__class__.__name__} saving.')
    hash_ = file_hasher(cache_path)

    res_path = RESOURCE_DIR + hash_ + ext
    if not os.path.isfile(res_path):
        from shutil import move
        move(cache_path, res_path)
    else:
        os.remove(cache_path)

    return res_path


def local_data_loader(filename: str):
    if RESOURCE_DIR not in filename:
        path = RESOURCE_DIR + filename
        for ext in ['.npy', '.npz']:
            if os.path.isfile(path + ext):
                path += ext
                break
        else:
            raise ValueError(f'Cannot find valid resource file with filename / hash: {filename}')
    else:
        path = filename

    if path.endswith('.npy'):
        return np.load(path)
    elif path.endswith('.npz'):
        return sparse.load_npz(path)
    else:
        raise NotImplementedError(f'`local_data_loader` does not support {path} loading.')
