# -*- coding: utf-8 -*-

from __future__ import absolute_import

from threading import Thread
from oasis.datasource import DataSource
from oasis.libs.log import logger
from oasis.models import Models

THREAD_JOIN_TIMEOUT = 5


class Job(object):
    """Job defines config for calculation job."""
    def __init__(self, id, data_source,
                 models, slack_channel):
        self.id = id
        self.data_source = DataSource(data_source["url"])
        self.models = models
        self.slack_channel = slack_channel
        self.running_models = []
        self.threads = dict()

    def to_dict(self):
        return {
            "id": self.id,
            "data_source": self.data_source.to_dict(),
            "models": self.models,
            "slack_channel": self.slack_channel
        }

    def run(self):
        logger.info("[job:{job}] start to run"
                    .format(job=self.to_dict()))
        for md in self.models:
            model = Models[md.get("name")]
            model_runner = model(self.id, md, self.data_source, self.slack_channel)
            t = Thread(target=model_runner.run())
            t.start()
            self.running_models.append(model_runner)
            self.threads[md.get("name")] = t

    def close(self):
        logger.info("[job-id:{job_id}] start to stop"
                    .format(job_id=self.id))
        for model in self.running_models:
            model.close()

        for model in self.threads:
            self.threads[model].join(THREAD_JOIN_TIMEOUT)

    def valid(self):
        # check job
        if self.id == "":
            return False

        if self.slack_channel is None \
                or self.slack_channel == "":
            return False

        if self.models is None \
                or len(self.models) == 0:
            return False

        for model in self.models:
            if "name" not in model:
                return False

            if model.get("name") not in Models:
                return False

        return True


