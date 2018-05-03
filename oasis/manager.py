# -*- coding: utf-8 -*-

from __future__ import absolute_import

from threading import Lock
from oasis.storage import new_sqlite_storage
from oasis.libs.log import logger
from oasis.controller import Controller
from oasis.models import Models
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

    def new_job(self, data_source, models, slack_channel, timeout):
        with self.lock:
            models_name = []
            for model in models:
                if model.get('name') not in Models:
                    raise ModelNotSupportException
                models_name.append(model.get('name'))

            job = self.storage.set_job({
                'data_source': data_source,
                'models': ',' .join(models_name),
                'timeout': timeout,
                'slack_channel': slack_channel,
                'status': JOB_PENDING,
                'reports': '',
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

    def list_all_job(self):
        with self.lock:
            return self.storage.list_jobs()

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
            job = self.storage.get_job(job_id)

            if job is None:
                raise JobNotExistsException(job_id)

            return job

    def get_job_report(self, job_id):
        with self.lock:
            job = self.storage.get_job(job_id)
            logger.info(job)

            if job is None:
                raise JobNotExistsException(job_id)

            return job.get('reports')

    def close(self):
        logger.info("closing the server")
        with self.lock:
            self.controller.close()

