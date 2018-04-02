# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

from oasis.models.model import Model
from oasis.datasource import PrometheusAPI, PrometheusQuery, Metrics


class Rules(Model):
    def __init__(self, job, callback):
        self.job = job
        self.callback = callback
        self.api = PrometheusAPI(job.data_source)



