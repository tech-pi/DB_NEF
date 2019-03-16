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

import attr
import type

_tiny = 1e-8

_huge = 1e8

TYPE_BIND = {}


class DataClass:
    '''`DataClass` is suited for storing data objects. It is the most basic class type in
    `srfnef` package. All data and functions would be seriously considered to be defined as a
    Dataclass instance. More specific, only the field `.data` in a `DataClass` would be regarded
    as the only computable part with in an instance. Any other class that defined to contained
    data would a subclass of `DataClass`.
    '''

    def replace(self, **kwargs):
        '''Creates a new object of the same type of instance, replacing fields with values from
        changes.
        '''
        return attr.evolve(self, **kwargs)

    @classmethod
    def fields(cls):
        '''Returns a tuple of field names for this `DataClass` instance.
        '''
        return attr.fields_dict(cls)

    def as_dict(self, recurse = True):
        '''Return a dictionary of fields for this 'DataClass` instance.
        '''
        return attr.asdict(self, recurse)

    def to_tuple(self):
        '''Return a tuple of fields for this 'DataClass` instance.
        '''
        return attr.astuple(self)

    def register(self, func):
        obj = self.replace()
        if isinstance(func, list):
            for f in func:
                obj = f(obj)
        elif callable(func):
            obj = func(obj)
        else:
            raise ValueError('func argument must be callable or a list of callables')
        return obj

    @classmethod
    def class_register(cls, func):
        _cls = cls
        if isinstance(func, list):
            for f in func:
                _cls = f(_cls)
        elif callable(func):
            _cls = func(_cls)
        else:
            raise ValueError('func argument must be callable or a list of callables')
        return _cls


def dataclass(cls):
    '''This function is a decorator that is used to add generated special methods to classes, as
    described below.

    The `dataclass()` decorator examines the class to find fields. A field is defined as class
    variable that has a type annotation. The order of the fields in all of the generated methods
    is the order in which they appear in the class definition.
    Be default the instance decorated by `dataclass` is attributed frozen, which means we prefer
    it to be immutable.

    Some basic arithmetic operators are mounted and would apply on `.data` field.
    '''
    base = attr.s(auto_attribs = True)(cls)
    return type(base.__name__, (base, DataClass), {})
