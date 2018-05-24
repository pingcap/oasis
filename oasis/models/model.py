# -*- coding: utf-8 -*-

from __future__ import absolute_import

import yaml
import time
import urlparse
from threading import Event, Lock
from oasis.libs.log import logger
from oasis.libs.alert import send_to_slack

THREAD_JOIN_TIMEOUT = 5
REPORT_ADDRESS = ""

MODEL_NEW = "new"
MODEL_RUNNING = "running"
MODEL_STOP = "stop"
MODEL_ERROR = "error"
MODEL_FINISH = "finish"


class Model(object):
    """Model is a abstract of calculation model."""
    def __init__(self, name, md_instance, store, cfg):
        self.name = name
        self.md_instance = md_instance
        self.store = store
        self.cfg = cfg
        self.threads = dict()
        self.event = Event()
        self.lock = Lock()
        self._exit = False
        self.status = MODEL_NEW
        self.report = ModelReport(self.name, md_instance.get('job_id'), self.cfg.to_dict())
        self.log_prefix = "[job-id:{id}][model:{model}]"\
            .format(id=md_instance.get('job_id'), model=name)

    def run(self):
        logger.info("run model")

    def close(self):
        with self.lock:
            self._exit = True
            self.event.set()
            for key in self.threads:
                self.threads[key].join(THREAD_JOIN_TIMEOUT)

    def save_model(self):
        self.md_instance['status'] = self.status
        self.md_instance['report'] = self.report.to_dict()

        self.store.set_model_instance(self.md_instance)

    def get_report(self):
        return None

    def get_id(self):
        return self.md_instance.get('id')

    def send_to_slack(self, message, slack_channel): 
        send_to_slack(message+"\n"+"Job Detail: {url}"
                .format(urlparse.urljoin(REPORT_ADDRESS, 
                        "/detail?id={job_id}"
                                .format(job_id=self.md_instance.get("job_id")))), slack_channel) 

    @staticmethod
    def get_model_template(name, model_path):
        config_file = "{path}/{name}.yml".format(path=model_path, name=name)
        with open(config_file, 'r') as yml_file:
            cfg = yaml.load(yml_file)

        return cfg
    

class Config(object):
    def __init__(self, model_template, config_json=None):
        self.model = dict()
        self.metrics = dict()
        self.config_json = config_json

        # set default config
        self._set_default_config()

        self._parse_data(model_template)

        # load config from json data
        if self.config_json is not None:
            self._parse_api_config()

    def _parse_api_config(self):
        self._parse_data(self.config_json)

    def _parse_data(self, data):
        for section in data:
            if section == "model":
                for key in data[section]:
                    self.model[key] = data[section][key]
            elif section == "metrics":
                for key in data[section]:
                    self.metrics[key] = data[section][key]

    def _set_default_config(self):
        logger.info("set default config")

    def to_dict(self):
        return {
            "model": self.model,
            "metrics": self.metrics
        }


class ModelReport(object):
    def __init__(self, model_name, job_id, model_config):
        self.job_id = job_id
        self.model_name = model_name
        self.model_config = model_config
        self.start_time = time.asctime(time.localtime(time.time()))
        self.metrics_report = dict()

    def to_dict(self):
        return {
            "job_id": self.job_id,
            "model_name": self.model_name,
            "model_config": self.model_config,
            "start_time": self.start_time,
            "metrics_report": self.metrics_report
        }


