# encoding: utf-8
'''
@author: Minghao Guo
@contact: mh.guo0111@gmail.com
@software: srf_ct
@file: typing.py
@date: 3/15/2019
@desc:
'''
# encoding: utf-8
'''
srfnef.templating
~~~~~~~~~~~~~~~~~

This module provides basic data and function types of the whole package,
including `dataclass` for data and `funcclass` for functions.

`DataClass`, as well as `FuncClass`, instances `io` to `.hdf5` files are implemented in `save`
and `load` natual modes.
'''
from sqlalchemy import Column, Integer, Float, String, Boolean, ForeignKey
from sqlalchemy.dialects import postgresql
import dataclasses
import numpy as np
import attr
import typing

_tiny = 1e-8

_huge = 1e8

TYPE_BIND = {}


def is_dataclass(cls):
    try:
        cls.fields()
        return True
    except:
        return False


table_support_type = {
    int: int,
    np.int64: int,
    np.int32: int,
    float: float,
    np.float32: float,
    np.float64: float,
    bool: bool,
    str: str,
    np.ndarray: list,
    typing.List[str]: list,
    typing.List[int]: list,
    typing.List[float]: list
}
