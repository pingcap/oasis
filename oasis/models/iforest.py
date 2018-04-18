# -*- coding: utf-8 -*-

from __future__ import absolute_import

import time
import numpy as np
import pandas as pd
import datetime
import random
from oasis.datasource import PrometheusAPI, PrometheusQuery, Metrics
from sklearn.ensemble import IsolationForest
from threading import Timer, Thread
from pytimeparse.timeparse import timeparse
from oasis.models.model import Model, Config, ModelReport
from oasis.libs.log import logger
from oasis.libs.features import Features
from oasis.libs.alert import send_to_slack

IFOREST_MODEL_NAME = "iForest"


class IForest(Model):
    def __init__(self, job_id, model, data_source, slack_channel, timeout):
        super(IForest, self).__init__(IFOREST_MODEL_NAME, job_id)
        self.api = PrometheusAPI(data_source)
        self.slack_channel = slack_channel
        self.df = dict()
        self.ilf = dict()
        self.timer = Timer(timeparse(timeout), self.timeout_action)
        self.metrics = model.get("metrics")
        self.config_file = "%s/iforest.yml" % self.model_path
        self.cfg = IForestConfig(self.config_file,
                                 model.get("config", None))
        self.report = ModelReport(self.name, job_id, self.cfg.to_dict())

    def train(self, metric, query_expr, config):
        logger.info("{log_prefix}[metric:{metric}] starting to get sample data"
                    .format(log_prefix=self.log_prefix, metric=metric))
        self.df[metric] = pd.DataFrame(columns=config["features"])
        self.ilf[metric] = IsolationForest(n_estimators=100, verbose=2)
        for index in range(0, self.cfg.model["train_count"], 1):
            if self._exit:
                logger.info("{log_prefix}[metric:{metric}] stop"
                            .format(log_prefix=self.log_prefix, metric=metric))
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

                logger.info("{log_prefix}[metric:{metric}] append data to train df:{df_one}"
                            .format(log_prefix=self.log_prefix,
                                    metric=metric, df_one=df_one))

            self.event.wait(timeparse(self.cfg.model["train_interval"]))
        logger.info("{log_prefix}[metric:{metric}] starting to train sample data"
                    .format(log_prefix=self.log_prefix, metric=metric))
        self.ilf[metric].fit(self.df[metric][config["features"]])
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

            logger.info("{log_prefix}[metric:{metric}] append data to train df:{df_one}"
                        .format(log_prefix=self.log_prefix, metric=metric, df_one=df_one))
            self.df[metric] = self.df[metric].append(df_one, ignore_index=True)

    def predict(self, metric, query_expr, config):
        logger.info("{log_prefix}[metric:{metric}] starting to predict"
                    .format(log_prefix=self.log_prefix, metric=metric))
        while not self._exit:
            now = datetime.datetime.now()
            query = PrometheusQuery(query_expr,
                                    time.mktime((now - datetime.timedelta(minutes=10)).timetuple()),
                                    time.mktime(now.timetuple()), "15s")

            with self.lock:
                self.report.metrics_report[metric]["predict_count"] = \
                    self.report.metrics_report[metric]["predict_count"] + 1

            is_match, predict_data = self.predict_task(metric, query, config)
            if is_match == 1:
                logger.info("{log_prefix}[metric:{metric}] predict OK"
                            .format(log_prefix=self.log_prefix, metric=metric))
            else:
                with self.lock:
                    self.report.metrics_report[metric]["predict_errors"].append({
                        "metric": metric,
                        "time": now,
                        "message": "predict metric {metric} error".format(metric=metric),
                        "predict_data": predict_data,
                    })

                self.on_error(metric, predict_data)

            self.event.wait(timeparse(self.cfg.model["predict_interval"]))

        logger.info("{log_prefix}[metric:{metric}] stop"
                    .format(log_prefix=self.log_prefix, metric=metric))

    def predict_task(self, metric, query, config):
        data_set = self.api.query(query)
        values = []
        for data in data_set.values():
            values.append(float(data))

        df_one = []
        for key in config["features"]:
            if key in Features:
                df_one.append(Features[key](values))

        predict_data = np.array([df_one])

        logger.info("{log_prefix}[metric:{metric}] predict data:{predict_data}"
                    .format(log_prefix=self.log_prefix,
                            metric=metric, predict_data=predict_data))

        return self.ilf[metric].predict(predict_data), df_one

    def run(self):
        logger.info("{log_prefix} start to run"
                    .format(log_prefix=self.log_prefix, model=self.name))
        self.timer.start()
        for metric in self.metrics:
            if metric not in Metrics:
                logger.error("{log_prefix}[metric:{metric}] is not supported"
                             .format(log_prefix=self.log_prefix, metric=metric))
                continue

            val = Metrics[metric]
            if metric not in self.cfg.metrics:
                logger.error("{log_prefix}[metric:{metric}] can't found the config of this metric"
                             .format(log_prefix=self.log_prefix, metric=metric))
                continue

            self.report.metrics_report[metric] = {
                "predict_count": 0,
                "predict_errors": [],
            }

            t = Thread(target=self.run_action,
                       args=(metric, val, self.cfg.metrics[metric]))
            t.start()
            self.threads[metric] = t

    def run_action(self, metric, val, config):
        logger.info("{log_prefix}[metric:{metric}] start to run"
                    .format(log_prefix=self.log_prefix, metric=metric))
        if self.train(metric, val, config):
            self.predict(metric, val, config)

    def close(self):
        # TODO: close this job
        logger.info("{log_prefix} closing"
                    .format(log_prefix=self.log_prefix))
        super(IForest, self).close()
        self.timer.cancel()

    def timeout_action(self):
        logger.info("{log_prefix} finish the model"
                    .format(log_prefix=self.log_prefix))
        super(IForest, self).close()

    def on_error(self, metric, predict_data):
        logger.info("{log_prefix}[metric:{metric}] Predict Error, predict data:{predict_data}"
                    .format(log_prefix=self.log_prefix,
                            metric=metric, predict_data=predict_data))
        send_to_slack("{log_prefix}[model:{model}], predict metric {metric} error, "
                      "predict data:{predict_data}"
                      .format(log_prefix=self.log_prefix,
                              model=self.name, metric=metric, predict_data=predict_data),
                      self.slack_channel)

    def get_report(self):
        with self.lock:
            return self.report.to_dict()


class IForestConfig(Config):
    def __init__(self, config_file, config_json=None):
        super(IForestConfig, self).__init__(config_file, config_json)

    def _set_default_config(self):
        self.model.setdefault("train_count", 120)
        self.model.setdefault("train_interval", "60s")
        self.model.setdefault("predict_interval", "5m")

        for metric in Metrics.keys():
            self.metrics[metric] = {
                "features": ["mean", "std"],
                "rules": ["features[std] > 1000"]
            }

