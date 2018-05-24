# -*- coding: utf-8 -*-

from __future__ import absolute_import

import os
import sqlite3
import json
import datetime
from oasis.storage.sql import SCHEMA
from oasis.models.util import json_serial


class SQLite(object):
    def __init__(self, db_path):
        self.db_path = os.path.expanduser(db_path)
        self.executescript(SCHEMA)

        self.model_template = ModelTemplate(self)
        self.model_instance = ModelInstance(self)
        self.job = Job(self)

    def execute(self, sql, args=()):
        if isinstance(sql, (list, tuple)):
            sql = ' '.join(sql)

        with sqlite3.connect(self.db_path) as con:
            return con.execute(sql, args)

    def executescript(self, sqls):
        with sqlite3.connect(self.db_path) as con:
            return con.executescript(sqls)


class ModelTemplate(object):
    """Hopefully DB-independend SQL to store, modify and retrieve all
       model_template related actions.  Here's a short scheme overview:

           | id     | name        | config  |
           +--------+-------------+---------+
           | 0      | iForest     | xxxxxx  |
           | 1      | rules       | xxxxxx  |
           +--------+-------------+---------+

       The id is primary key and name is unique.
       """
    fields = ['id', 'name', 'config']

    def __init__(self, db):
        self.db = db

    def add(self, m):
        self.db.execute(
            'INSERT INTO model_template (name, config) VALUES (?, ?);',
            (m.get('name'),
             str(json.dumps(m.get('config'), default=json_serial))))

        return self.get(m.get('name'))

    def update(self, m):
        self.db.execute(
            ['UPDATE model_template SET', '   config = ?', 'WHERE name = ?;'],
            (str(m.get('config')), m.get('name')))

        return self.get(m.get('name'))

    def get(self, name):
        data = self.db.execute('SELECT * FROM model_template WHERE name = ?;',
                               (name, )).fetchone()

        if data is not None:
            return dict(zip(self.fields, data))

        return None

    def list(self):
        data = self.db.execute('SELECT * FROM model_template;').fetchall()

        models = []

        for item in data:
            models.append(dict(zip(self.fields, item)))

        return models


class ModelInstance(object):
    """Hopefully DB-independend SQL to store, modify and retrieve all
       model_instance related actions.  Here's a short scheme overview:

           | id     | model   | job_id  | report   | status  |
           +--------+---------+---------+----------+---------+
           | 0      | iForest | 1       | xxxxxxxx | running |
           | 1      | rules   | 1       | xxxxxxxx | running |
           +--------+---------+---------+----------+---------+

       The id is primary key.
       """
    fields = ['id', 'model', 'job_id', 'report', 'status']

    def __init__(self, db):
        self.db = db

    def add(self, m):
        stmt = self.db.execute([
            'INSERT INTO model_instance (', '   model, job_id,'
            '   report, status)', 'VALUES (?, ?, ?, ?);'
        ], (m.get('model'), m.get('job_id'),
            str(json.dumps(m.get('report'), default=json_serial)),
            m.get('status')))

        m['id'] = stmt.lastrowid
        return m

    def update(self, m):
        self.db.execute([
            'UPDATE model_instance SET', '   model = ?, job_id = ?,',
            '   report = ?, status = ?', 'WHERE id = ?;'
        ], (m.get('model'), m.get('job_id'),
            str(json.dumps(m.get('report'), default=json_serial)),
            m.get('status'), m.get('id')))

        return self.get(m.get('id'))

    def get(self, id):
        data = self.db.execute('SELECT * FROM model_instance WHERE id = ?;',
                               (id, )).fetchone()

        if data is not None:
            return dict(zip(self.fields, data))

        return None

    def list(self):
        data = self.db.execute('SELECT * FROM model_instance;').fetchall()

        models = []

        for item in data:
            models.append(dict(zip(self.fields, item)))

        return models


class Job(object):
    """Hopefully DB-independend SQL to store, modify and retrieve all
       job actions.  Here's a short scheme overview:

           | id     | name         | models         | ...... | status |
           +--------+--------------+----------------+----------+---------+
           | 0      | xxxxxxx      | iforest,rules  | ...... | running |
           | 1      | xxxxxxxx     | iforest        | ...... | running |
           +--------+--------------+----------------+--------+---------+

       The id is primary key.
    """
    fields = [
        'id', 'name', 'data_source', 'models', 'timeout', 'slack_channel',
        'model_instance_ids', 'status', 'api_models_config', 'start_time'
    ]

    def __init__(self, db):
        self.db = db

    def add(self, job):
        now = datetime.datetime.now()
        stmt = self.db.execute([
            'INSERT INTO job (', '   name, data_source, models, timeout,',
            '   slack_channel, model_instance_ids,'
            '   status, api_models_config, start_time)',
            'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);'
        ], (job.get('name'),
            str(json.dumps(job.get('data_source'), default=json_serial)),
            job.get('models'), job.get('timeout'), job.get('slack_channel'),
            job.get('model_instance_ids'), job.get('status'),
            str(json.dumps(job.get('api_models_config'), default=json_serial)),
            now))

        return self.get(stmt.lastrowid)

    def update(self, job):
        self.db.execute([
            'UPDATE job SET ', '   data_source = ?, models = ?, timeout = ?,',
            '   slack_channel = ?,model_instance_ids = ?,',
            '   status = ?, api_models_config = ?', 'WHERE id = ?;'
        ], (str(json.dumps(job.get('data_source'), default=json_serial)),
            job.get('models'), job.get('timeout'), job.get('slack_channel'),
            job.get('model_instance_ids'), job.get('status'),
            str(json.dumps(job.get('api_models_config'), default=json_serial)),
            job.get('id')))
        return self.get(job.get('id'))

    def get(self, id):
        data = self.db.execute('SELECT * FROM job WHERE id = ?;',
                               (id, )).fetchone()

        if data is not None:
            return dict(zip(self.fields, data))

        return None

    def get_by_name(self, name):
        data = self.db.execute('SELECT * FROM job WHERE name = ?;',
                               (name, )).fetchone()

        if data is not None:
            return dict(zip(self.fields, data))

        return None

    def list(self):
        data = self.db.execute('SELECT * FROM job;').fetchall()

        jobs = []

        for item in data:
            jobs.append(dict(zip(self.fields, item)))

        return jobs
