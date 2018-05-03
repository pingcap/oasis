# -*- coding: utf-8 -*-

from __future__ import absolute_import

import urlparse
from threading import Thread, Timer, Lock, Event
from pytimeparse.timeparse import timeparse
from oasis.datasource import DataSource
from oasis.libs.log import logger
from oasis.models import Models
from oasis.libs.alert import send_to_slack
from oasis.models.model import MODEL_NEW


DEFAULT_JOB_TIMEOUT = "240h"
THREAD_JOIN_TIMEOUT = 5
REPORT_ADDRESS = ""
SYNC_INTERVAL = "1m"

JOB_PENDING = 'pending'
JOB_RUNNING = "running"
JOB_ERROR = "error"
JOB_FINISHED = "finished"
JOB_STOPPED = "stopped"


class Job(object):
    """Job defines config for calculation job."""
    def __init__(self, store, data):
        self.store = store
        self.id = data.get('id')
        self.data_source = DataSource(data.get('data_source')['url'])
        self.models_name = data.get('models').strip().split(',')
        self.api_models_config = data.get('api_models_config')
        self.slack_channel = data.get('slack_channel')
        self.timeout = data.get('timeout')
        self.status = data.get('status')
        self.running_models = []
        self.report = dict()
        self.threads = dict()
        self.timer = None
        self.lock = Lock()
        self.sync_thread = Thread(target=self.sync)
        self._exit = False
        self.event = Event()

    def to_dict(self):
        return {
            "id": self.id,
            "data_source": self.data_source.to_dict(),
            "api_models_config": self.api_models_config,
            "slack_channel": self.slack_channel
        }

    def save_job(self):
        model_ids = []
        for md in self.running_models:
            model_ids.append(str(md.get_id()))

        self.store.set_job({
            'id': self.id,
            'data_source': self.data_source.to_dict(),
            'models': ','.join(self.models_name),
            'slack_channel': self.slack_channel,
            'timeout': self.timeout,
            'reports': str(self.report),
            'model_instance_ids': ','.join(model_ids),
            'status': self.status,
            'api_models_config': self.api_models_config
        })

    def run(self):
        with self.lock:
            logger.info("[job:{job}] start to run"
                        .format(job=self.to_dict()))
            try:
                for md in self.api_models_config:
                    model = Models[md.get("name")]
                    md_instance = self.store.set_model_instance({
                        'job_id': self.id,
                        'model': md.get("name"),
                        'report': '',
                        'status': MODEL_NEW
                    })
                    model_runner = model(md_instance, self.store, md, self.data_source, self.slack_channel, self.timeout)
                    t = Thread(target=model_runner.run)
                    t.start()
                    self.running_models.append(model_runner)
                    self.threads[md.get("name")] = t
            except Exception as e:
                logger.info("[job:{job}] fail to star: {err}"
                            .format(job=self.to_dict(), err=str(e)))
                logger.exception("Exception Logged")
                self.status = JOB_ERROR
            else:
                self.timer = Timer(timeparse(self.timeout), self.timeout_action)
                self.status = JOB_RUNNING
            finally:
                self.save_job()

        logger.info("[job-id:{job_id}] start to sync"
                    .format(job_id=self.id))
        self.sync_thread.start()

    def close(self):
        with self.lock:
            logger.info("[job-id:{job_id}] start to stop"
                        .format(job_id=self.id))
            try:
                self._exit = True
                self.event.set()

                for model in self.running_models:
                    model.close()

                for model in self.threads:
                    self.threads[model].join(THREAD_JOIN_TIMEOUT)

                self.timer.cancel()
                self.sync_thread.join()
            except Exception as e:
                logger.info("[job-id:{job_id}] fail to stop: {err}"
                            .format(job_id=self.id, err=str(e)))
                self.status = JOB_ERROR
            else:
                self.status = JOB_STOPPED
            finally:
                self.save_job()

    def valid(self):
        # check job
        with self.lock:
            if self.id == "":
                return False

            if self.slack_channel is None \
                    or self.slack_channel == "":
                return False

            if self.api_models_config is None \
                    or len(self.api_models_config) == 0:
                return False

            for model in self.api_models_config:
                if "name" not in model:
                    return False

                if model.get("name") not in Models:
                    return False

            return True

    def sync(self):
        while not self._exit:
            self.sync_report()
            self.save_job()
            self.event.wait(timeparse(SYNC_INTERVAL))

        logger.info("[job-id:{job_id}] stop to sync"
                    .format(job_id=self.id))

    def sync_report(self):
        with self.lock:
            model_reports = dict()
            for model in self.running_models:
                model_reports[model.name] = model.get_report()

            self.report = {
                "id": self.id,
                "data_source": self.data_source.to_dict(),
                "models": self.models_name,
                "slack_channel": self.slack_channel,
                "model_report": model_reports
            }

    def timeout_action(self):
        logger.info("[job:{job}] finish"
                    .format(job=self.to_dict()))

        self.status = JOB_FINISHED
        self.save_job()

        send_to_slack("{job:{job} finish \n. report detail: {url}"
                      .format(job=self.to_dict(),
                              url=urlparse.urljoin(REPORT_ADDRESS,
                                                   "api/v1/job/{job_id}/report"
                                                   .format(job_id=self.id))))



