# -*- coding: utf-8 -*-

from __future__ import absolute_import

import yaml
from threading import Event, Lock
from oasis.libs.log import logger
from oasis.models.util import sub_id

MODELS_PATH = ""
THREAD_JOIN_TIMEOUT = 5


class Model(object):
    """Model is a abstract of calculation model."""
    def __init__(self):
        self.threads = dict()
        self.event = Event()
        self.lock = Lock()
        self._exit = False
        self.model_path = MODELS_PATH

    def run(self):
        logger.info("run model")

    def close(self):
        with self.lock:
            self._exit = True
            self.event.set()
            for key in self.threads:
                self.threads[key].join(THREAD_JOIN_TIMEOUT)


class Config(object):
    def __init__(self, config_file, config_json=None):
        self.model = dict()
        self.metrics = dict()
        self.config_file = config_file
        self.config_json = config_json

        # set default config
        self._set_default_config()

        # load config from config file
        self._parse_config_file()

        # load config from json data
        if self.config_json is not None:
            self._parse_api_config()

    def _parse_config_file(self):
        with open(self.config_file, 'r') as yml_file:
            cfg = yaml.load(yml_file)

        self._parse_data(cfg)

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

