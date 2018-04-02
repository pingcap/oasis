# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

from oasis.datasource import DataSource

DEFAULT_JOB_TIMEOUT = "240h"


class Job(object):
    """Job defines config for calculation job."""
    def __init__(self, id, data_source,
                 model, metrics, slack_channel, timeout=DEFAULT_JOB_TIMEOUT):
        self.id = id
        self.data_source = DataSource(data_source["url"])
        self.model = model
        self.metrics = metrics
        self.slack_channel = slack_channel
        self.timeout = timeout
    # def __init__(self, data):
    # self.__dict__ = json.loads(data)

    def __iter__(self):
        yield "id", self.id
        yield "data_source", dict(self.data_source)
        yield "model", self.model
        yield "metrics", self.metrics
        yield "slack_channel", self.slack_channel
        yield "timeout", self.timeout
        # return self.__dict__
