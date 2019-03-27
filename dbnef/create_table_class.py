from sqlalchemy import Column, Integer, Float, String, Boolean
from sqlalchemy.dialects import postgresql
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
import typing

from .utils import convert_Camal_to_snake, TABLE_TYPE_BIND, is_dataclass, fields
from .config import Base


def create_table_class(cls: type):
    assert is_dataclass(cls)
    table_name = convert_Camal_to_snake(cls.__name__)
    table_class_name = cls.__name__ + 'Table'
    if table_class_name in TABLE_TYPE_BIND.keys():
        table_cls = TABLE_TYPE_BIND[table_class_name]
    else:
        kwargs = {'__tablename__': table_name,
                  'id': Column(Integer, primary_key = True)}
        kwargs.update(({'datetime': Column(String)}))
        kwargs.update(({'creator': Column(String)}))
        kwargs.update(({'status': Column(String)}))
        kwargs.update({'labels': Column(postgresql.ARRAY(String, dimensions = 1))})
        for spec in fields(cls):
            key = spec.name
            if key == 'data':
                kwargs.update({'res_id': Column(Integer, ForeignKey('resources.id'))})
                kwargs.update({key: relationship('ResourceTable')})
            else:
                if spec.type is int:
                    kwargs.update({key: Column(Integer, nullable = True)})
                elif spec.type is float:
                    kwargs.update({key: Column(Float, nullable = True)})
                elif spec.type is bool:
                    kwargs.update({key: Column(Boolean, nullable = True)})
                elif spec.type is str:
                    kwargs.update({key: Column(String, nullable = True)})
                elif spec.type is typing.List[float]:
                    kwargs.update(
                        {key: Column(postgresql.ARRAY(Float, dimensions = 1), nullable = True)})
                elif spec.type is typing.List[int]:
                    kwargs.update(
                        {key: Column(postgresql.ARRAY(Integer, dimensions = 1), nullable = True)})
                elif spec.type is typing.List[str]:
                    kwargs.update(
                        {key: Column(postgresql.ARRAY(String, dimensions = 1), nullable = True)})
                elif spec.type is typing.List[bool]:
                    kwargs.update(
                        {key: Column(postgresql.ARRAY(Boolean, dimensions = 1), nullable = True)})
                elif spec.type is list:
                    kwargs.update(
                        {key: Column(postgresql.ARRAY(Float, dimensions = 1), nullable = True)})
                elif is_dataclass(spec.type):
                    sub_table_class = create_table_class(spec.type)
                    sub_table_name = sub_table_class.__tablename__
                    kwargs.update({sub_table_name + '_id': Column(Integer, ForeignKey(
                        sub_table_name + '.id'))})
                    kwargs.update({key: relationship(spec.type.__name__ + 'Table')})
                else:
                    raise NotImplementedError(f'type {spec.type} is not implemented yet.')
        kwargs.update({'hash_': Column(String, nullable = True)})
        table_cls = type(table_class_name, (Base,), kwargs)
        TABLE_TYPE_BIND.update({table_class_name: table_cls})
    return table_cls


def create_table(cls: type):
    table_cls = create_table_class(cls)

    Base.metadata.create_all()
    return table_cls
