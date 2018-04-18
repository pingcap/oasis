# -*- coding: utf-8 -*-

from __future__ import absolute_import

import datetime
import time
from threading import Thread, Timer
from pytimeparse.timeparse import timeparse
from oasis.models.model import Model, Config, ModelReport
from oasis.datasource import PrometheusAPI, PrometheusQuery, Metrics
from oasis.libs.log import logger
from oasis.models.util import EPS
from oasis.libs.features import Features
from oasis.libs.alert import send_to_slack
from oasis.libs.rules import parse_rule, OPERATORS

RULES_MODEL_NAME = "rules"


class Rules(Model):
    def __init__(self, job_id, model, data_source, slack_channel, timeout):
        super(Rules, self).__init__(RULES_MODEL_NAME, job_id)
        self.api = PrometheusAPI(data_source)
        self.slack_channel = slack_channel
        self.timer = Timer(timeparse(timeout), self.timeout_action)
        self.metrics = model.get("metrics")
        self.config_file = "%s/rules.yml" % self.model_path
        self.cfg = RulesConfig(self.config_file, model.get("config", None))
        self.report = ModelReport(self.name, job_id, self.cfg.to_dict())

    def run(self):
        logger.info("{log_prefix} start to run"
                    .format(log_prefix=self.log_prefix))
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
                       args=(metric, val, self.cfg.metrics[metric],
                             self.cfg.rules[metric]))
            t.start()
            self.threads[metric] = t

    def run_action(self, metric, val, config, rules):
        logger.info("{log_prefix}[metric:{metric}] start ot run"
                    .format(log_prefix=self.log_prefix, metric=metric))
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
                logger.info("{log_prefix}[metric:{metric}] extraction features {value}, "
                            "start to match with rule"
                            .format(log_prefix=self.log_prefix,
                                    metric=metric, value=features_value))
                with self.lock:
                    self.report.metrics_report[metric]["predict_count"] = \
                        self.report.metrics_report[metric]["predict_count"] + 1

                is_match, not_match_rule = self.match_rules(metric, features_value, rules)
                if not is_match:
                    with self.lock:
                        self.report.metrics_report[metric].append({
                            "metric": metric,
                            "time": datetime.datetime.now(),
                            "features_value": features_value,
                            "not_match_rule": not_match_rule,
                        })

                    self.on_error(metric, not_match_rule)

            self.event.wait(timeparse(self.cfg.model["predict_interval"]))

        logger.info("{log_prefix}[metric:{metric}] stop"
                    .format(log_prefix=self.log_prefix, metric=metric))

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
        not_match_rule = None
        for rule in rules:
            if rule["feature"] not in features_value:
                continue

            if check_is_triggered(features_value[rule["feature"]],
                                  rule["operator"], rule["value"]):
                match_flag = False
                not_match_rule = rule
                break

        if match_flag:
            logger.info("{log_prefix}[metric:{metric}] predict OK"
                        .format(log_prefix=self.log_prefix, metric=metric))

        return match_flag, not_match_rule

    def close(self):
        logger.info("{log_prefix} closing"
                    .format(log_prefix=self.log_prefix))
        super(Rules, self).close()
        self.timer.cancel()

    def timeout_action(self):
        logger.info("{log_prefix} finish the model"
                    .format(log_prefix=self.log_prefix))
        super(Rules, self).close()

    def on_error(self, metric, rule):
        logger.error("{log_prefix}[metric:{metric}] not match rule: {rule}"
                     .format(log_prefix=self.log_prefix, metric=metric, rule=rule))
        send_to_slack("{log_prefix}[model:{model}][metric:{metric}] not match rule: {rule}"
                      .format(log_prefix=self.log_prefix,
                              model=self.name, metric=metric,
                              rule=rule), self.slack_channel)

    def get_report(self):
        with self.lock:
            return self.report.to_dict()


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
        ">": (lambda: left_value > right_value)
    }.get(operator, lambda: False)()

