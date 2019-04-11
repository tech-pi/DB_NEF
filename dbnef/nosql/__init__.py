# encoding: utf-8
'''
@author: Minghao Guo
@contact: mh.guo0111@gmail.com
@software: srf_ct
@file: __init__.py
@date: 4/9/2019
@desc:
'''
from .add import add
from .create_nosql_table import create_nosql_table, NosqlTable
from .delete import delete_with_hash, delete, clear_nosql_table
from .query import query_with_hash, search, query
from .update import update_with_hashes, update
