# -*- coding: utf-8 -*-

from __future__ import absolute_import

from threading import Lock
from oasis.storage import new_sqlite_storage
from oasis.libs.log import logger
from oasis.controller import Controller
from oasis.models import Models
from oasis.datasource.prometheus import Metrics
from oasis.job import (
    JOB_PENDING,
    JOB_RUNNING
)

from oasis.libs.iexceptions import (
    JobNotExistsException,
    ModelNotSupportException
)

MODELS_PATH = ""


class Manager(object):
    def __init__(self, db_path):
        self.lock = Lock()
        self.storage = new_sqlite_storage(db_path)
        self.controller = Controller(self.storage)

        if not (MODELS_PATH == ""):
            self.init_model_template()

    def init_model_template(self):
        logger.info("init model templates")

        for name, model in Models.items():
            cfg = model.get_model_template(name, MODELS_PATH)
            self.storage.set_model_template({
                "name": name,
                "config": str(cfg)
            })

    def new_job(self, name, data_source, models, slack_channel, timeout):
        with self.lock:
            models_name = []
            for model in models:
                if model.get('name') not in Models:
                    raise ModelNotSupportException
                models_name.append(model.get('name'))

            job = self.storage.set_job({
                'name': name,
                'data_source': data_source,
                'models': ',' .join(models_name),
                'timeout': timeout,
                'slack_channel': slack_channel,
                'status': JOB_PENDING,
                'model_instance_ids': '',
                'api_models_config': models
            })

            self.controller.run_job(job)
            return job

    def stop_job(self, job_id):
        with self.lock:
            job = self.storage.get_job(job_id)

            if job is None:
                raise JobNotExistsException(job_id)

            self.controller.stop_job(job)

    def stop_job_by_name(self, name):
        with self.lock:
            job = self.storage.get_job_by_name(name)

            if job is None:
                raise JobNotExistsException

            self.controller.stop_job(job)

    def get_jobs_len(self):
        with self.lock:
            return len(sorted(self.storage.list_jobs(), key=lambda j: j['id'], reverse=True))

    def list_jobs(self, offset, size):
        with self.lock:
            jobs = sorted(self.storage.list_jobs(), key=lambda j: j['id'], reverse=True)

            jobs_len = len(jobs)
            if offset > jobs_len:
                return []

            if offset+size > jobs_len:
                return jobs[offset:]
            else:
                return jobs[offset:offset+size]

    def list_running_job(self):
        with self.lock:
            jobs = self.storage.list_jobs()

            running_jobs = []

            for job in jobs:
                if job.get('status') == JOB_RUNNING:
                    running_jobs.append(job)

            return running_jobs

    def get_job(self, job_id):
        with self.lock:
            job_store = self.storage.get_job(job_id)

            if job_store is None:
                raise JobNotExistsException(job_id)

            job = job_store
            job["model_instances"] = []

            instance_ids_str = job.get('model_instance_ids')
            if instance_ids_str is not None:
                md_instance_ids = instance_ids_str.split(',')
                for md_id in md_instance_ids:
                    if md_id == '':
                        continue

                    instance = self.storage.get_model_instance(md_id)
                    if instance is None:
                        continue

                    job["model_instances"].append(instance)

            return job

    def list_model_templates(self, offset, size):
        with self.lock:
            templates = self.storage.list_model_templates()

            templates_len = len(templates)
            if offset > templates_len:
                return []

            if offset+size > templates_len:
                return templates[offset:]
            else:
                return templates[offset:offset+size]

    def list_metrics(self, offset, size):
        with self.lock:
            metrics = []
            for metric, query in Metrics.items():
                metrics.append({
                    "name": metric,
                    "query": query
                })

            metrics_len = len(metrics)
            if offset > metrics_len:
                return []

            if offset+size > metrics_len:
                return metrics[offset:]
            else:
                return metrics[offset:offset+size]

    def close(self):
        logger.info("closing the server")
        with self.lock:
            self.controller.close()
