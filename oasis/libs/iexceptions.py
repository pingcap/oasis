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


class NewJobException(Exception):
    def __init__(self, job, message):
        pass


class JobNotRunningException(Exception):
    def __init__(self, job):
        pass


class TaskTypeNotSupportedException(Exception):
    def __init__(self, task):
        pass


class CloseJobException(Exception):
    def __init__(self):
        pass
