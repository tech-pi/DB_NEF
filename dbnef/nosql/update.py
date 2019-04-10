# encoding: utf-8
'''
@author: Minghao Guo
@contact: mh.guo0111@gmail.com
@software: srf_ct
@file: update.py
@date: 4/10/2019
@desc:
'''
# encoding: utf-8
'''
@author: Minghao Guo
@contact: mh.guo0111@gmail.com
@software: srf_ct
@file: update_labels.py
@date: 3/25/2019
@desc:
'''
from .add import add_keywords
from .delete import delete_with_hash
from .query import search


def update_with_hashes(hsh: str = None, *, kw: dict = None):
    if hsh is None or kw is None:
        return 0

    delete_with_hash(hsh, fields = list(kw.keys()))
    add_keywords(hsh, kw = kw)
    return 1


def update(filters: dict = None, *, kw: dict = None):
    if filters is None:
        return 0
    hashes = search(filters)
    for hsh in hashes:
        update_with_hashes(hsh, kw = kw)
    return 1
