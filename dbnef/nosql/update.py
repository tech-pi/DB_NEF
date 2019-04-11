from dbnef.utils import load_schema
from .add import add_keywords
from .delete import delete_with_hash
from .query import search

schema_dict = load_schema()


def update_with_hashes(hsh: str = None, *, kw: dict = None, mode = 'new', schema_check = True):
    if hsh is None or kw is None:
        return 0
    if mode == 'new':
        delete_with_hash(hsh, fields = list(kw.keys()), schema_check = schema_check)
        add_keywords(hsh, kw = kw, schema_check = schema_check)
    elif mode == 'add':
        add_keywords(hsh, kw = kw, schema_check = schema_check)
    else:
        raise NotImplementedError
    return 1


def update(filters: dict = None, *, kw: dict = None, mode = 'new', schema_check = True):
    if filters is None:
        return 0
    hashes = search(filters)
    for hsh in hashes:
        update_with_hashes(hsh, kw = kw, mode = mode, schema_check = schema_check)
    return 1
