# encoding: utf-8
"""
@author: Minghao Guo
@contact: mh.guo0111@gmail.com
@software: srf_ct
@file: config.py
@date: 3/13/2019
@desc:
"""
from contextlib import contextmanager

from sqlalchemy.orm import sessionmaker

ws1_engine_url = 'postgresql://postgres:postgres@192.168.1.111/nef_db'
ws2_engine_url = 'postgresql://postgres:postgres@localhost/pitech_nosql_test'


@contextmanager
def create_engine(engine_url = ws2_engine_url):
    from sqlalchemy import create_engine
    engine = create_engine(engine_url, echo = False)
    try:
        yield engine
    except:
        pass
    finally:
        pass


@contextmanager
def create_session(*, engine_url = ws2_engine_url, is_commit = True):
    with create_engine(engine_url) as engine:
        Session = sessionmaker(bind = engine)
        session = Session()
        try:
            yield session
        except:
            pass
        finally:
            if is_commit:
                session.commit()
            session.close()


@contextmanager
def create_base_class(engine_url = ws2_engine_url):
    from sqlalchemy.ext.declarative import declarative_base
    with create_engine(engine_url) as engine:
        try:
            Base = declarative_base()
            Base.metadata.bind = engine
            yield Base
        except:
            pass
        finally:
            pass
