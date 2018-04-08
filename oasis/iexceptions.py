# -*- coding: utf-8 -*-

from __future__ import absolute_import


class ModelNotSupportException(Exception):
    def __init__(self, model_name):
        pass


class JobNotExistsException(Exception):
    def __init__(self, job_id):
        pass

