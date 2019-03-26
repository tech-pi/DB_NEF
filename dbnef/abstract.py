# encoding: utf-8
'''
@author: Minghao Guo
@contact: mh.guo0111@gmail.com
@software: srf_ct
@file: abstract.py
@date: 3/22/2019
@desc:
'''
import graphene


class Abstract(graphene.AbstractType):
    name: graphene.String()
    creation_datetime: graphene.types.datetime.DateTime()
    labels: graphene.List(graphene.String)
    __hash__: graphene.String()


class Resource(graphene.AbstractType, Abstract):
    pass


class Object(graphene.AbstractType, Abstract):
    pass


class Task(graphene.AbstractType, Abstract):
    pass
