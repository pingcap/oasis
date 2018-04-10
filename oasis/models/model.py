# -*- coding: utf-8 -*-

from __future__ import absolute_import

from oasis.libs.log import logger
from oasis.datasource.data_model import DataSource
# import json

MODELS_PATH = ""


class Model(object):
    """Model is a abstract of calculation model."""
    def __init__(self):
        self.model_path = MODELS_PATH

    def run(self):
        logger.info("running calculation model")

    def close(self):
        logger.info("close model")



