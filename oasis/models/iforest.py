# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

import time
import numpy as np
import pandas as pd
import datetime
import random
from threading import Thread
from oasis.datasource import PrometheusAPI, PrometheusQuery, Metrics
from sklearn.ensemble import IsolationForest
from threading import Event, Lock, Timer
from pytimeparse.timeparse import timeparse
from oasis.models.model import Model
from oasis.models.util import sub_id
from oasis.libs.log import logger


class IForest(Model):
    def __init__(self, job, callback):
        self.job = job
        self.callback = callback
        self.api = PrometheusAPI(job.data_source)
        self.df = dict()
        self.ilf = dict()
        # TODO: make them configurable.
        self.train_count = 120
        self.train_interval = 60
        self.predict_interval = 300

        self.event = Event()
        self.lock = Lock()
        self.__exit = False
        self.timer = Timer(timeparse(self.job.timeout), self.timeout_action)

    def train(self, metric, query_expr):
        logger.info("[job-id:{id}][metric:{metric}] starting to get sample data"
                    .format(id=sub_id(self.job.id), metric=metric))
        self.df[metric] = pd.DataFrame(columns=["mean", "std"])
        self.ilf[metric] = IsolationForest(n_estimators=100,
                                           n_jobs=-1, verbose=2)
        for index in range(0, self.train_count, 1):
            if self.__exit:
                logger.info("[job-id:{id}][metric:{metric}] stop"
                            .format(id=sub_id(self.job.id), metric=metric))
                return False

            now = datetime.datetime.now()
            query = PrometheusQuery(query_expr,
                                    time.mktime((now - datetime.timedelta(minutes=15)).timetuple()),
                                    time.mktime(now.timetuple()), "15s")
            self.train_task(metric, query)

            if index % 10 == 0:
                mean_value = float(random.randint(0, 5000))
                std_value = float(random.randint(0, 10000))
                df_one = {"mean": mean_value, "std": std_value}
                self.df[metric] = self.df[metric].append(df_one, ignore_index=True)

                logger.info("[job-id:{id}][metric:{metric}] append data to train df:{df_one}"
                            .format(id=sub_id(self.job.id), metric=metric, df_one=df_one))

            self.event.wait(self.train_interval)
        x_cols = ["mean", "std"]
        logger.info("[job-id:{id}][metric:{metric}] starting to train sample data"
                    .format(id=sub_id(self.job.id), metric=metric))
        self.ilf[metric].fit(self.df[x_cols])
        return True

    def train_task(self, metric, query):
        data_set = self.api.query(query)
        if len(data_set) > 0:
            values = []
            for data in data_set.values():
                values.append(float(data))

            mean_value = np.mean(values)
            std_value = np.std(values)
            df_one = {"mean": mean_value, "std": std_value}

            logger.info("[job-id:{id}][metric:{metric}] append data to train df:{df_one}"
                        .format(id=sub_id(self.job.id), metric=metric, df_one=df_one))
            self.df[metric] = self.df[metric].append(df_one, ignore_index=True)

    def predict(self, metric, query_expr):
        logger.info("[job-id:{id}][metric:metric}]starting to predict"
                    .format(id=sub_id(self.job.id), metric=metric))
        while not self.__exit:
            now = datetime.datetime.now()
            query = PrometheusQuery(query_expr,
                                    time.mktime((now - datetime.timedelta(minutes=5)).timetuple()),
                                    time.mktime(now.timetuple()), "15s")

            if self.predict_task(metric, query) == 1:
                logger.info("[job-id:{id}][metric:{metric}] predict OK"
                            .format(id=sub_id(self.job.id), metric=metric))
            else:
                logger.info("[job-id:{id}][metric:{metric}] Predict Error"
                            .format(id=sub_id(self.job.id), metric=metric))
                self.callback("[job] {job}, predict metric {metric} error in last {time}s"
                              .format(job=dict(self.job), metric=metric,
                                      time=self.predict_interval),
                              self.job.slack_channel)

            self.event.wait(self.predict_interval)
        logger.info("[job-id:{id}][metric:{metric}] stop"
                    .format(id=sub_id(self.job.id), metric=metric))

    def predict_task(self, metric, query):
        data_set = self.api.query(query)
        values = []
        for data in data_set.values():
            values.append(float(data))

        mean_value = np.mean(values)
        std_value = np.std(values)
        predict_data = np.array([[mean_value, std_value]])

        logger.info("[job-id:{id}][metric:{metric}] predict data:{predict_data}"
                    .format(id=sub_id(self.job.id),
                            metric=metric, predict_data=predict_data))
        return self.ilf[metric].predict(predict_data)

    def run(self):
        self.timer.start()
        for key in self.job.metrics:
            if key in Metrics:
                val = Metrics[key]
                # if self.train(val):
                #     self.predict(val)
                t = Thread(target=self.run_action, args=(key, val, ))
                t.start()

    def run_action(self, metric, val):
        if self.train(metric, val):
            self.predict(metric, val)

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





