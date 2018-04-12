# -*- coding: utf-8 -*-

from __future__ import absolute_import

import datetime
import time
from threading import Thread, Timer
from pytimeparse.timeparse import timeparse
from oasis.models.model import Model, Config
from oasis.datasource import PrometheusAPI, PrometheusQuery, Metrics
from oasis.libs.log import logger
from oasis.models.util import sub_id, EPS
from oasis.libs.features import Features
from oasis.libs.alert import send_to_slack
from oasis.libs.rules import parse_rule, OPERATORS


class Rules(Model):
    def __init__(self, job):
        super(Rules, self).__init__()
        self.job = job
        self.api = PrometheusAPI(job.data_source)
        self.timer = Timer(timeparse(self.job.timeout), self.timeout_action)
        self.config_file = "%s/rules.yml" % self.model_path
        self.cfg = RulesConfig(self.config_file, job.config)

    def run(self):
        self.timer.start()
        for key in self.job.metrics:
            if key in Metrics:
                val = Metrics[key]
                if key not in self.cfg.metrics:
                    continue

                t = Thread(target=self.run_action,
                           args=(key, val, self.cfg.metrics[key],
                                 self.cfg.rules[key]))
                t.start()
                self.threads[key] = t

    def run_action(self, metric, val, config, rules):
        logger.info("[job-id:{id}][metric:{metric}] start ot run"
                    .format(id=sub_id(self.job.id), metric=metric))
        self.compute(metric, val, config, rules)

    def compute(self, metric, query_expr, config, rules):
        """Extraction features and match with rules

        First: get metric from data source
        Second: extraction features from metrics
        Third: use features to match with all rules about this metric,
               if not match, will send a alert to slack
        """
        while not self._exit:
            data_set = self.query_data(query_expr)
            if len(data_set) > 0:
                features_value = self.extraction_features(data_set, config)
                logger.info("[job-id:{id}][metric:{metric}] extraction features {value}, "
                            "start to match with rule"
                            .format(id=sub_id(self.job.id),
                                    metric=metric, value=features_value))
                self.match_rules(metric, features_value, rules)

            self.event.wait(timeparse(self.cfg.model["predict_interval"]))

        logger.info("[job-id:{id}][metric:{metric}] stop"
                    .format(id=sub_id(self.job.id), metric=metric))

    def query_data(self, query_expr):
        now = datetime.datetime.now()
        query = PrometheusQuery(query_expr,
                                time.mktime((now - datetime.timedelta(
                                    seconds=timeparse(self.cfg.model["data_range"])))
                                            .timetuple()),
                                time.mktime(now.timetuple()), "15s")
        return self.api.query(query)

    def extraction_features(self, data_set, config):
        values = []
        for data in data_set.values():
            values.append(float(data))

        features_value = {}
        for key in config["features"]:
            if key in Features:
                features_value[key] = Features[key](values)

        return features_value

    def match_rules(self, metric, features_value, rules):
        match_flag = True
        for rule in rules:
            if rule["feature"] not in features_value:
                continue

            if check_is_triggered(features_value[rule["feature"]],
                                  rule["operator"], rule["value"]):
                logger.error("[job-id:{id}][metric:{metric}] not match rule: {rule}"
                             .format(id=sub_id(self.job.id), metric=metric, rule=rule))
                send_to_slack("[job] {job}, metric: {metric} not match rule: {rule}"
                              .format(job=dict(self.job), metric=metric,
                                      rule=rule), self.job.slack_channel)
                match_flag = False
                break

        if match_flag:
            logger.info("[job-id:{id}][metric:{metric}] predict OK"
                        .format(id=sub_id(self.job.id), metric=metric))

    def close(self):
        logger.info("[job-id:{id}] closing the job"
                    .format(id=sub_id(self.job.id)))
        super(Rules, self).close()
        self.timer.cancel()

    def timeout_action(self):
        logger.info("[job-id:{id}] finish the job"
                    .format(id=sub_id(self.job.id)))
        super(Rules, self).close()


class RulesConfig(Config):
    def __init__(self, config_file, config_json=None):
        super(RulesConfig, self).__init__(config_file, config_json)
        self.rules = dict()
        self._parse_rules()

    def _set_default_config(self):
        self.model.setdefault("data_range", "10m")
        self.model.setdefault("predict_interval", "5m")

        for metric in Metrics.keys():
            self.metrics[metric] = {
                "features": ["mean", "std"],
                "rules": ["features[std] > 1000"]
            }

    def _parse_rules(self):
        for metric in self.metrics:
            rules = self.metrics[metric].get("rules")
            self.rules[metric] = parse_rule(rules)


def check_is_triggered(left_value, operator, right_value):
    if operator not in OPERATORS:
        logger.error("operator {} is invalid".format(operator))
        return False

    return {
        "==": (lambda: abs(left_value-right_value) < EPS),
        "!=": (lambda: abs(left_value-right_value) > EPS),
        "<=": (lambda: left_value <= right_value),
        ">=": (lambda: left_value >= right_value),
        "=": (lambda: abs(left_value-right_value) < EPS),
        "<": (lambda: left_value < right_value),
        ">": (lambda: left_value > right_value),
    }.get(operator, lambda: False)()

