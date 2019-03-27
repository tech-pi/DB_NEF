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
import numpy as np
import typing

# required py3.7 installed
from dataclasses import is_dataclass, fields

