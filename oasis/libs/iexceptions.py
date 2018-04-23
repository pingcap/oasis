# -*- coding: utf-8 -*-

from __future__ import absolute_import


class ParseRuleException(Exception):
    def __init__(self, rule):
        pass


class ModelNotSupportException(Exception):
    def __init__(self, model_name):
        pass


class JobNotExistsException(Exception):
    def __init__(self, job_id):
        pass


class AddModelException(Exception):
    def __init__(self, message):
        pass


class LoadDataException(Exception):
    def __init__(self, message):
        pass

