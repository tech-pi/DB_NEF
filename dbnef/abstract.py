# encoding: utf-8
'''
@author: Minghao Guo
@contact: mh.guo0111@gmail.com
@software: srf_ct
@file: abstract.py
@date: 3/22/2019
@desc:
'''
from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects import postgresql

from .config import Base
from .utils import TABLE_TYPE_BIND


class ResourceTable(Base):
    __tablename__ = 'resources'
    id = Column(Integer, primary_key = True)
    datetime = Column(String)
    creator = Column(String)
    status = Column(String)
    labels = Column(postgresql.ARRAY(String, dimensions = 1))
    url = Column(String, nullable = False, unique = True)
    hash_ = Column(String, nullable = False, unique = True)


def create_resource_table():
    table_cls = ResourceTable
    Base.metadata.create_all()
    TABLE_TYPE_BIND.update({'ResourceTable': ResourceTable})


class TaskTable(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key = True)
    datetime = Column(String)
    creator = Column(String)
    status = Column(String)
    depends = Column(postgresql.ARRAY(String, dimensions = 1))
    labels = Column(postgresql.ARRAY(String, dimensions = 1))
    hash_ = Column(String, nullable = False, unique = True)
    function = Column(String)
    arguments = Column(postgresql.ARRAY(String, dimensions = 1))


def create_task_table():
    table_cls = TaskTable
    Base.metadata.create_all()
    TABLE_TYPE_BIND.update({'TaskTable': TaskTable})
