# -*- coding: utf-8 -*-

from __future__ import absolute_import

import time
import numpy as np
import pandas as pd
import datetime
import random
import yaml
import os
from threading import Thread
from oasis.datasource import PrometheusAPI, PrometheusQuery, Metrics
from sklearn.ensemble import IsolationForest
from threading import Event, Lock, Timer
from pytimeparse.timeparse import timeparse
from oasis.models.model import Model
from oasis.models.util import sub_id
from oasis.libs.log import logger
from oasis.libs.features import Features


IFOREST_CONFIG_FILE = "%s/iforest.yml" % os.path.dirname(__file__)


class IForest(Model):
    def __init__(self, job, callback):
        self.job = job
        self.callback = callback
        self.api = PrometheusAPI(job.data_source)
        self.df = dict()
        self.ilf = dict()
        self.event = Event()
        self.lock = Lock()
        self.__exit = False
        self.timer = Timer(timeparse(self.job.timeout), self.timeout_action)
        # TODO: make them configurable.
        self.cfg = IForestConfig(job.config)

    def train(self, metric, query_expr, config):
        logger.info("[job-id:{id}][metric:{metric}] starting to get sample data"
                    .format(id=sub_id(self.job.id), metric=metric))
        self.df[metric] = pd.DataFrame(columns=config["features"])
        self.ilf[metric] = IsolationForest(n_estimators=100, verbose=2)
        for index in range(0, self.cfg.model["train_count"], 1):
            if self.__exit:
                logger.info("[job-id:{id}][metric:{metric}] stop"
                            .format(id=sub_id(self.job.id), metric=metric))
                return False

            now = datetime.datetime.now()
            query = PrometheusQuery(query_expr,
                                    time.mktime((now - datetime.timedelta(minutes=15)).timetuple()),
                                    time.mktime(now.timetuple()), "15s")
            self.train_task(metric, query, config)

            if index % 10 == 0:
                df_one = {}
                for key in config["features"]:
                    if key in Features:
                        df_one[key] = float(random.randint(0, 10000))
                self.df[metric] = self.df[metric].append(df_one, ignore_index=True)

                logger.info("[job-id:{id}][metric:{metric}] append data to train df:{df_one}"
                            .format(id=sub_id(self.job.id), metric=metric, df_one=df_one))

            self.event.wait(self.cfg.model["train_interval"])
        logger.info("[job-id:{id}][metric:{metric}] starting to train sample data"
                    .format(id=sub_id(self.job.id), metric=metric))
        self.ilf[metric].fit(self.df[metric])
        return True

    def train_task(self, metric, query, config):
        data_set = self.api.query(query)
        if len(data_set) > 0:
            values = []
            for data in data_set.values():
                values.append(float(data))

            df_one = {}
            for key in config["features"]:
                if key in Features:
                    df_one[key] = Features[key](values)

            logger.info("[job-id:{id}][metric:{metric}] append data to train df:{df_one}"
                        .format(id=sub_id(self.job.id), metric=metric, df_one=df_one))
            self.df[metric] = self.df[metric].append(df_one, ignore_index=True)

    def predict(self, metric, query_expr, config):
        logger.info("[job-id:{id}][metric:{metric}]starting to predict"
                    .format(id=sub_id(self.job.id), metric=metric))
        while not self.__exit:
            now = datetime.datetime.now()
            query = PrometheusQuery(query_expr,
                                    time.mktime((now - datetime.timedelta(minutes=5)).timetuple()),
                                    time.mktime(now.timetuple()), "15s")

            if self.predict_task(metric, query, config) == 1:
                logger.info("[job-id:{id}][metric:{metric}] predict OK"
                            .format(id=sub_id(self.job.id), metric=metric))
            else:
                logger.info("[job-id:{id}][metric:{metric}] Predict Error"
                            .format(id=sub_id(self.job.id), metric=metric))
                self.callback("[job] {job}, predict metric {metric} error in last {time}s"
                              .format(job=dict(self.job), metric=metric,
                                      time=self.cfg.model["predict_interval"]),
                              self.job.slack_channel)

            self.event.wait(self.cfg.model["predict_interval"])
        logger.info("[job-id:{id}][metric:{metric}] stop"
                    .format(id=sub_id(self.job.id), metric=metric))

    def predict_task(self, metric, query, config):
        data_set = self.api.query(query)
        values = []
        for data in data_set.values():
            values.append(float(data))

        df_one = {}
        for key in config["features"]:
            if key in Features:
                df_one[key] = Features[key](values)

        predict_data = np.array([df_one.values()])

        logger.info("[job-id:{id}][metric:{metric}] predict data:{predict_data}"
                    .format(id=sub_id(self.job.id),
                            metric=metric, predict_data=predict_data))
        return self.ilf[metric].predict(predict_data)

    def run(self):
        self.timer.start()
        for key in self.job.metrics:
            if key in Metrics:
                val = Metrics[key]
                config = {"features": ["mean", "std"]}
                if key in self.cfg.metrics and "features" in self.cfg.metrics[key]:
                    config = self.cfg.metrics[key]

                t = Thread(target=self.run_action, args=(key, val, config, ))
                t.start()

    def run_action(self, metric, val, config):
        if self.train(metric, val, config):
            self.predict(metric, val, config)

    def close(self):
        # TODO: close this job
        with self.lock:
            logger.info("[job-id:{id}] closing the job"
                        .format(id=sub_id(self.job.id)))
            self.__exit = True
            self.event.set()

            self.timer.cancel()

    def timeout_action(self):
        # TODO: do some clean action after timeout
        with self.lock:
            logger.info("[job-id:{id}] finish the job"
                        .format(id=sub_id(self.job.id)))
            self.__exit = True
            self.event.set()


class IForestConfig(object):
    def __init__(self, config=None):
        self.model = dict()
        self.metrics = dict()

        # load config from config file
        self._parse_config_file()

        # load config from json data
        if config is not None:
            self._parse_api_config(config)

        # set default value
        self._set_default_config()

    def _set_default_config(self):
        self.model.setdefault("train_count", 120)
        self.model.setdefault("train_interval", 60)
        self.model.setdefault("predict_interval", 300)

    def _parse_config_file(self):
        with open(IFOREST_CONFIG_FILE, 'r') as ymlfile:
            cfg = yaml.load(ymlfile)

        if "model" in cfg:
            self.model = cfg["model"]

        if "metrics" in cfg:
            self.metrics = cfg["metrics"]

    def _parse_api_config(self, config):
        for section in config:
            if section == "model":
                for key in config[section]:
                    self.model[key] = config[section][key]
            elif section == "metrics":
                for key in config[section]:
                    self.metrics[key] = config[section][key]



