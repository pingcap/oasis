# -*- coding: utf-8 -*-

from __future__ import absolute_import

from threading import Lock
from oasis.libs.log import logger
from oasis.libs.iexceptions import LoadDataException


class Storage(object):
    def __init__(self, client):
        self.client = client
        self.lock = Lock()

        # cache data
        self.model_templates = dict()
        self.model_instances = dict()
        self.jobs = dict()

        # load data to cache
        try:
            self.load()
        except Exception as e:
            assert LoadDataException(str(e))

    def load(self):
        with self.lock:
            logger.info("start to load data")

            # load model templates
            mts = self.client.model_template.list()

            for model in mts:
                self.model_templates[model.get('name')] = model

            # load model instances
            mis = self.client.model_instance.list()

            for instance in mis:
                self.model_instances[instance.get('id')] = instance

            # load job
            jobs = self.client.job.list()

            for job in jobs:
                self.jobs[job.get('id')] = job

    def set_model_template(self, m):
        with self.lock:
            model_tmp = self.client.model_template.get(m.get('name'))
            if model_tmp is None:
                model = self.client.model_template.add(m)
            else:
                model = self.client.model_template.update(m)

            self.model_templates[model.get('name')] = model

            return model

    def get_model_template(self, name):
        with self.lock:
            return self.model_templates.get(name)

    def list_model_templates(self):
        with self.lock:
            models = []

            for name in self.model_templates:
                models.append(self.model_templates.get(name))

            return models

    def set_model_instance(self, m):
        with self.lock:
            if m.get('id') is None:
                instance = self.client.model_instance.add(m)
            else:
                instance = self.client.model_instance.update(m)

            self.model_instances[instance.get('id')] = instance

            return instance

    def get_model_instance(self, id):
        with self.lock:
            return self.model_instances.get(int(id))

    def list_model_instances(self):
        with self.lock:

            instances = []

            for id in self.model_instances:
                instances.append(self.model_instances.get(id))

            return instances

    def set_job(self, job):
        with self.lock:
            if job.get('id') is None:
                job_new = self.client.job.add(job)
            else:
                job_new = self.client.job.update(job)

            self.jobs[job_new.get('id')] = job_new

            return job_new

    def get_job(self, id):
        with self.lock:
            return self.jobs.get(int(id))

    def get_job_by_name(self, name):
        with self.lock:
            return self.jobs.get_by_name(name)

    def list_jobs(self):
        with self.lock:
            jobs = []

            for id in self.jobs:
                jobs.append(self.client.job.get(id))

            return jobs


