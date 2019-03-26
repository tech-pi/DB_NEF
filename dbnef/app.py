# encoding: utf-8
'''
@author: Minghao Guo
@contact: mh.guo0111@gmail.com
@software: srf_ct
@file: app.py
@date: 3/25/2019
@desc:
'''
import dbnef as db
import srfnef as nef


@nef.typing.dataclass
class BankAccount:
    val: int


@nef.typing.dataclass
class Person:
    name: str
    val: int
    account: BankAccount


table_class = db.create_table_class(Person)

import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from dbnef.utils import TABLE_TYPE_BIND


class Person(SQLAlchemyObjectType):
    class Meta:
        model = TABLE_TYPE_BIND['PersonTable']
        interfaces = (relay.Node,)


class PersonConnection(relay.Connection):
    class Meta:
        node = Person


class BankAccount(SQLAlchemyObjectType):
    class Meta:
        model = TABLE_TYPE_BIND['BankAccountTable']
        interfaces = (relay.Node,)


class BankAccountConnections(relay.Connection):
    class Meta:
        node = BankAccount


class Query(graphene.ObjectType):
    node = relay.Node.Field()
    # Allows sorting over multiple columns, by default over the primary key
    all_persons = SQLAlchemyConnectionField(PersonConnection)
    # Disable sorting over this field
    all_bank_accounts = SQLAlchemyConnectionField(BankAccountConnections, sort = None)


# def schema():
#     return graphene.Schema(query = Query)
schema = graphene.Schema(query = Query)

# flask_sqlalchemy/app.py
from flask import Flask
from flask_graphql import GraphQLView

app = Flask(__name__)
app.debug = True
app.add_url_rule(
    '/graphql',
    view_func = GraphQLView.as_view(
        'graphql',
        schema = schema,
        graphiql = True  # for having the GraphiQL interface
    )
)


@app.teardown_appcontext
def shutdown_session(exception = None):
    from dbnef.config import create_scoped_session
    create_scoped_session().remove()


if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 5000)
