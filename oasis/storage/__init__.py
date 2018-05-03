# -*- coding: utf-8 -*-

from __future__ import absolute_import

from oasis.storage.storage import Storage
from oasis.storage.sqlite import SQLite


def new_sqlite_storage(db_path):
    return Storage(SQLite(db_path))