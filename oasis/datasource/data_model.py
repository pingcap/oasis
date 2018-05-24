# -*- coding: utf-8 -*-

from __future__ import absolute_import

from oasis.libs.log import logger


class DataModel(object):
    """DataModel is a abstract of data source.

    data source, eg: prometheus
    """

    def query(self, query):
        logger.info("dataMode query: {query}".format(query=query))


class DataSource(object):
    """DataSource defines config for data source."""

    def __init__(self, url):
        self.url = url

    def to_dict(self):
        return {"url": self.url}
