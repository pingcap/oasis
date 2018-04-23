# -*- coding: utf-8 -*-

from oasis.storage.storage import Storage
from oasis.storage.sqlite import SQLite


def new_sqlite_storage(db_path):
    return Storage(SQLite(db_path))